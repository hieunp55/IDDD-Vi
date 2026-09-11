Calendar sẽ khởi tạo một Aggregate (cụm đối tượng liên kết có ranh giới nhất quán) mới, cụ thể là CalendarEntry. Instance mới này sẽ được trả về cho client sau khi Event (sự kiện) CalendarEntryScheduled được phát hành (publish). (Chi tiết về Event được phát hành không mang nhiều ý nghĩa đối với nội dung thảo luận này.) Bạn có thể nhận thấy phương thức này không có các guard (điều kiện bảo vệ / kiểm tra tính hợp lệ trước khi thực thi) ở đầu hàm. Việc đặt guard cho chính Factory Method (phương thức khởi tạo đối tượng) là không cần thiết, bởi vì constructor của từng tham số Value Object (đối tượng giá trị) và constructor của CalendarEntry, cũng như các phương thức setter mà constructor tự ủy quyền (self-delegate) tới, đều đã cung cấp đầy đủ các guard cần thiết. (Xem Chương 5: Entities để biết thêm chi tiết về self-delegation và guard.) Nếu muốn cẩn thận hơn nữa, bạn vẫn có thể bổ sung thêm các guard tại đây.

Đội ngũ phát triển đã đặt tên phương thức bám sát theo Ubiquitous Language (ngôn ngữ chung / toàn hiện). Các chuyên gia nghiệp vụ (domain experts) cùng với các thành viên khác trong nhóm đã thảo luận về kịch bản sau:

Lịch sẽ lên lịch cho các mục lịch (Calendars schedule calendar entries).

Nếu thiết kế chỉ hỗ trợ một public constructor trên CalendarEntry, tính biểu đạt của mô hình sẽ bị suy giảm và chúng ta sẽ không thể mô hình hóa rõ ràng phần ngôn ngữ nghiệp vụ đó. Áp dụng thiết kế này đòi hỏi constructor toàn diện của Aggregate phải được ẩn hoàn toàn khỏi các client. Chúng tôi khai báo constructor với phạm vi protected, buộc client phải sử dụng Factory Method scheduleCalendarEntry() trên Calendar:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000441_e20911c0804f01adf87dff3ef77b3d5defee61e1348f15c1b9c35b0c897546b4.png)

```java
public class CalendarEntry extends Entity {
    ...
    protected CalendarEntry(
        Tenant aTenant,
        CalendarId aCalendarId,
        CalendarEntryId aCalendarEntryId,
        Owner anOwner,
        String aSubject,
        String aDescription,
        TimeSpan aTimeSpan,
        Alarm anAlarm,
        Repetition aRepetition,
        String aLocation,
        Set<Invitee> anInvitees) {
        ...
    }
    ...
}

```

Dù mang lại nhiều ưu điểm như quy trình khởi tạo chặt chẽ, giảm bớt gánh nặng sử dụng cho client và xây dựng được một mô hình giàu tính biểu đạt, việc sử dụng Factory Method trên Calendar cũng có nhược điểm là làm tăng thêm một chút chi phí hiệu năng (performance overhead). Tương tự như bất kỳ Aggregate Factory Method nào khác, Calendar sẽ phải được truy xuất từ kho lưu trữ dữ liệu (persistence store) trước khi có thể dùng để tạo CalendarEntry. Lần truy vấn bổ sung này hoàn toàn xứng đáng để đánh đổi, nhưng khi lưu lượng truy cập trong Bounded Context (ngữ cảnh giới hạn) này tăng lên, nhóm phát triển sẽ phải cân nhắc kỹ lưỡng các hệ quả đi kèm.

Một lợi ích thiết thực khác của việc sử dụng Factory là client không cần phải truyền vào hai trong số các tham số của constructor CalendarEntry. Với tổng cộng 11 tham số bắt buộc trong constructor, thiết kế này giúp giải phóng client khi chỉ yêu cầu cung cấp 9 tham số. Hầu hết 9 tham số này đều tương đối dễ khởi tạo đối với client. (Phải thừa nhận rằng việc tạo Set các instance Invitee có phức tạp hơn, nhưng đó không phải là lỗi của Factory Method. Nhóm phát triển nên tính đến việc thiết kế một tiện ích giúp cung cấp Set này thuận tiện hơn, điều này có thể mở ra hướng tiếp cận xây dựng một Factory chuyên biệt.)

Dù vậy, Tenant và CalendarId tương ứng luôn được cung cấp một cách nghiêm ngặt chỉ bởi Factory Method. Đây chính là nơi chúng ta đảm bảo rằng các instance CalendarEntry chỉ được tạo cho đúng Tenant và liên kết chính xác với Calendar tương ứng.

Bây giờ, hãy cùng xem xét thêm một ví dụ nữa từ Collaboration Context.

## Tạo các instance Discussion (Creating Discussion Instances)

Hãy xem Factory Method trên Forum. Nó có cùng động lực thúc đẩy và cách triển khai rất tương đồng với phương thức trên Calendar, vì vậy không cần đi quá sâu vào chi tiết. Tuy nhiên, việc áp dụng Factory Method ở đây còn mang lại một lợi thế bổ sung, như nhóm phát triển sẽ chứng minh dưới đây.

Hãy xem xét Factory Method startDiscussion() thể hiện rõ ngôn ngữ nghiệp vụ trên Forum:

```java
package com.saasovation.collaboration.domain.model.forum;

public class Forum extends Entity {
    ...
    public Discussion startDiscussion(
        DiscussionId aDiscussionId,
        Author anAuthor,
        String aSubject) {

        if (this.isClosed()) {
            throw new IllegalStateException("Forum is closed.");
        }

        Discussion discussion = new Discussion(
            this.tenant(),
            this.forumId(),
            aDiscussionId,
            anAuthor,
            aSubject);

        DomainEventPublisher
            .instance()
            .publish(new DiscussionStarted(...));

        return discussion;
    }
    ...
}

```

Bên cạnh việc khởi tạo Discussion, Factory Method này còn đóng vai trò guard nhằm ngăn chặn việc tạo mới nếu Forum đã bị đóng. Bản thân Forum sẽ tự cung cấp Tenant và ForumId liên kết. Nhờ đó, client chỉ cần truyền 3 trong số 5 tham số bắt buộc để khởi tạo một Discussion mới.

Factory Method này cũng thể hiện rõ Ubiquitous Language của Collaboration Context. Nhóm phát triển đã dùng startDiscussion() của Forum để thiết kế đúng theo những gì các chuyên gia nghiệp vụ diễn đạt:

Tác giả mở cuộc thảo luận trên diễn đàn (Authors start discussions on forums).

Điều này giúp mã nguồn phía client trở nên vô cùng đơn giản:

```java
Discussion discussion = agilePmForum.startDiscussion(
    this.discussionRepository.nextIdentity(),
    new Author("jdoe", "John Doe", "jdoe@saasovation.com"),
    "Dealing with Aggregate Concurrency Issues");

```

```java
assertNotNull(discussion);
...
this.discussionRepository.add(discussion);

```

Quả thực rất đơn giản — và đó luôn là mục tiêu hướng tới của một người làm mô hình hóa miền nghiệp vụ (domain modeler).

Pattern Factory Method này có thể lặp lại thường xuyên khi cần. Tôi tin rằng ví dụ trên đã chứng minh rõ ràng mức độ hiệu quả của các Factory Method đặt trên Aggregate trong việc thể hiện ngôn ngữ theo ngữ cảnh, giảm thiểu gánh nặng cho client khi tạo mới các instance Aggregate, đồng thời đảm bảo quá trình khởi tạo luôn đi kèm trạng thái hợp lệ.

## Factory trên Service (Factory on Service)

Vì phần lớn cách thức tôi sử dụng Service (dịch vụ miền) dưới dạng Factory đều liên quan đến nội dung Tích hợp các Bounded Context (Chương 13), nên tôi sẽ dành phần lớn dung lượng thảo luận cho chương đó. Trong chương 13, trọng tâm của tôi hướng nhiều hơn vào việc tích hợp với Anti-Corruption Layer (lớp chống tha hóa dữ liệu) (3), Published Language (ngôn ngữ chuẩn công bố) (3) và Open Host Service (dịch vụ máy chủ mở cung cấp giao thức chuẩn) (3). Tại đây, tôi muốn nhấn mạnh vào bản thân Factory và cách thiết kế một Service đóng vai trò là một Factory.

Nhóm phát triển tiếp tục đưa ra một ví dụ khác từ Collaboration Context. Đó là một Factory dưới dạng CollaboratorService, có nhiệm vụ sản sinh các instance Collaborator từ định danh của tenant và user:

```java
package com.saasovation.collaboration.domain.model.collaborator;

import com.saasovation.collaboration.domain.model.tenant.Tenant;

public interface CollaboratorService {
    public Author authorFrom(Tenant aTenant, String anIdentity);
    public Creator creatorFrom(Tenant aTenant, String anIdentity);
    public Moderator moderatorFrom(Tenant aTenant, String anIdentity);
    public Owner ownerFrom(Tenant aTenant, String anIdentity);

```

```java
    public Participant participantFrom(
        Tenant aTenant,
        String anIdentity);
}

```

Service này cung cấp khả năng chuyển đổi đối tượng từ Identity and Access Context sang Collaboration Context. Như đã trình bày trong Chương 2: Bounded Contexts, nhóm phát triển CollabOvation không dùng từ "user" (người dùng) khi thảo luận về tương tác cộng tác. Bản chất đúng hơn là: con người trong miền truyền thông cộng tác sẽ đóng vai trò là các tác giả (author), người sáng tạo (creator), người điều duyệt (moderator), chủ sở hữu (owner) và người tham gia (participant). Để hiện thực hóa điều này, nhóm cần tương tác với Identity and Access Context thông qua một Service và chuyển đổi các đối tượng user cùng role từ mô hình đó thành các đối tượng collaborator tương ứng trong Context của mô hình đội ngũ đang phát triển.

Vì các đối tượng mới kế thừa từ lớp cơ sở trừu tượng Collaborator đều do Service tạo ra, nên Service này thực chất hoạt động như một Factory. Xem xét việc triển khai một trong các phương thức của interface sẽ làm sáng tỏ các chi tiết liên quan:

```java
package com.saasovation.collaboration.infrastructure.services;

public class UserRoleToCollaboratorService implements CollaboratorService {
    public UserRoleToCollaboratorService() {
        super();
    }

    @Override
    public Author authorFrom(Tenant aTenant, String anIdentity) {
        return (Author) UserInRoleAdapter
            .newInstance()
            .toCollaborator(
                aTenant,
                anIdentity,
                "Author",
                Author.class);
    }
    ...
}

```

Vì đây là phần hiện thực hóa mang tính kỹ thuật, nên lớp này được đặt trong một Module (mô-đun đóng gói) (9) thuộc Infrastructure Layer (tầng hạ tầng).

Triển khai này gắn chặt với UserInRoleAdapter nhằm biến đổi một Tenant và một identity (tên người dùng của user) thành một instance thuộc lớp Author. Adapter (mẫu thiết kế bộ chuyển đổi) [Gamma et al.] này sẽ tương tác với Open Host Service của Identity and Access Context để xác nhận xem người dùng đó có đúng là thuộc role Author hay không. Nếu đúng, Adapter sẽ ủy quyền cho lớp CollaboratorTranslator thực hiện dịch phản hồi tích hợp dưới dạng Published Language thành một instance của lớp Author trong mô hình cục bộ. Lớp Author, cũng như các lớp con khác của Collaborator, đều là một Value Object đơn giản:

```java
package com.saasovation.collaboration.domain.model.collaborator;

```

```java
public class Author extends Collaborator {
    ...
}

```

Ngoại trừ constructor, equals(), hashCode() và toString(), mỗi lớp con đều kế thừa toàn bộ trạng thái và hành vi từ Collaborator:

```java
package com.saasovation.collaboration.domain.model.collaborator;

public abstract class Collaborator implements Serializable {
    private String emailAddress;
    private String identity;
    private String name;

    public Collaborator(
        String anIdentity,
        String aName,
        String anEmailAddress) {
        super();
        this.setEmailAddress(anEmailAddress);
        this.setIdentity(anIdentity);
        this.setName(aName);
    }
    ...
}

```

Collaboration Context sử dụng username làm thuộc tính định danh cho Collaborator. Các trường emailAddress và name chỉ là các instance String đơn giản. Trong mô hình này, nhóm phát triển lựa chọn giữ cho từng khái niệm này ở mức tối giản nhất có thể. Ví dụ, tên người dùng được lưu trữ đơn thuần dưới dạng chuỗi văn bản họ tên đầy đủ. Bằng cách sử dụng một Service-Based Factory, chúng ta đã tách biệt thành công vòng đời và hệ thống thuật ngữ khái niệm giữa hai Bounded Context.

Có một mức độ phức tạp nhất định bên trong UserInRoleAdapter và CollaboratorTranslator. Tóm lại, UserInRoleAdapter chỉ chịu trách nhiệm giao tiếp với Context bên ngoài. Trong khi đó, CollaboratorTranslator chỉ chịu trách nhiệm cho tác vụ chuyển dịch dẫn đến việc tạo mới đối tượng. Xem Chương 13: Integrating Bounded Contexts để biết thêm chi tiết.

## Tổng kết (Wrap-Up)

Chúng ta đã xem xét lý do tại sao nên sử dụng Factory trong DDD và cách chúng hòa nhập vào mô hình nghiệp vụ:

* Giờ đây bạn đã hiểu tại sao việc dùng Factory có thể tạo ra các mô hình giàu tính biểu đạt, bám sát hơn với Ubiquitous Language theo từng ngữ cảnh.
* Bạn đã thấy hai Factory Method khác nhau được triển khai dưới dạng các hành vi của Aggregate.
* Điều này giúp bạn học được cách sử dụng Factory Method để tạo các instance Aggregate thuộc kiểu khác, đồng thời luôn đảm bảo việc tạo ra và sử dụng dữ liệu nhạy cảm được diễn ra chính xác.
* Bạn cũng đã học được cách thiết kế Domain Service dưới dạng các Factory, thậm chí tương tác với các Bounded Context khác và chuyển đổi các đối tượng ngoại lai thành kiểu cục bộ.

Tiếp theo, chúng ta sẽ tìm hiểu cách thiết kế Repository (kho lưu trữ đối tượng) theo hai phong cách lưu trữ chính, cùng các lựa chọn triển khai khác cần được xem xét.

## Chương 12

## Repository (Kho lưu trữ)

Mắt em có màu giống hệt nhà kho của anh. — Nghe lỏm được tại một quán bar bình dân vùng nông thôn

> 💡 **Giải thích thêm:** Tác giả sử dụng một câu bông đùa bình dân ("redneck bar") mang tính chơi chữ và ẩn dụ mở đầu cho chủ đề. "Storage unit" (nhà kho cho thuê tự quản chứa đồ đạc) là hình ảnh đời thường gần gũi mô tả khái niệm "Repository" (kho lưu trữ đối tượng) trong phần mềm.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Một repository (kho lưu trữ) thường dùng để chỉ một địa điểm lưu trữ, thường được coi là nơi an toàn hoặc bảo quản các vật phẩm được cất giữ trong đó. Khi bạn lưu trữ một thứ gì đó vào kho và sau đó quay lại lấy, bạn kỳ vọng nó sẽ ở đúng trạng thái như khi bạn đặt nó vào. Đến một thời điểm nào đó, bạn có thể quyết định lấy vật phẩm đã cất ra khỏi kho.

Tập hợp các nguyên tắc cơ bản này áp dụng hoàn toàn cho Repository trong DDD. Khi đưa một instance của Aggregate (10) vào Repository tương ứng, rồi sau đó dùng chính Repository đó để lấy lại instance đó, bạn sẽ nhận lại nguyên vẹn đối tượng như mong đợi. Nếu bạn sửa đổi một instance Aggregate đã có sẵn mà bạn lấy ra từ Repository, các thay đổi của nó sẽ được lưu trữ bền vững (persisted). Nếu bạn xóa instance đó khỏi Repository, bạn sẽ không thể truy xuất lại nó kể từ thời điểm đó về sau.

> Đối với mỗi loại đối tượng cần truy cập toàn cục, hãy tạo một đối tượng có khả năng tạo ra ảo giác về một collection trong bộ nhớ chứa tất cả các đối tượng thuộc loại đó. Thiết lập quyền truy cập thông qua một interface toàn cục quen thuộc. Cung cấp các phương thức để thêm và xóa đối tượng. . . . Cung cấp các phương thức chọn lọc đối tượng dựa trên tiêu chí nào đó và trả về các đối tượng đã được khởi tạo hoàn chỉnh hoặc tập hợp các đối tượng có giá trị thuộc tính thỏa mãn tiêu chí. . . . Chỉ cung cấp repository cho các aggregate. . . . [Evans, tr. 151]

Các đối tượng giống như collection này hoàn toàn phục vụ cho mục đích lưu trữ dữ liệu (persistence). Mỗi kiểu Aggregate cần lưu trữ bền vững sẽ có một Repository tương ứng. Nói chung, tồn tại mối quan hệ một-một giữa một kiểu Aggregate và một Repository. Tuy nhiên, đôi khi hai hoặc nhiều kiểu Aggregate cùng chia sẻ một cấu trúc phân cấp đối tượng (object hierarchy), các kiểu này có thể dùng chung một Repository duy nhất. Cả hai cách tiếp cận này đều được thảo luận trong chương này.

## Lộ trình nội dung chương này (Road Map to This Chapter)

* Tìm hiểu về hai loại Repository khác nhau và lý do khi nào nên chọn loại này hay loại kia.
* Tìm hiểu cách hiện thực hóa Repository cho Hibernate, TopLink, Coherence và MongoDB.

còn tiếp

* Hiểu lý do tại sao bạn có thể cần thêm các hành vi bổ sung trên interface của Repository. Cân nhắc xem transaction (giao dịch) tương tác thế nào trong quá trình sử dụng Repository.
* Làm quen với các thách thức khi thiết kế Repository cho hệ thống phân cấp kiểu (type hierarchies).
* Xem xét một số khác biệt căn bản giữa Repository và Data Access Object (DAO - đối tượng truy cập dữ liệu) [Crupi et al.].
* Cân nhắc các cách thức kiểm thử Repository và cách viết test sử dụng Repository.

Nói một cách chặt chẽ, chỉ có Aggregate mới có Repository. Nếu bạn không sử dụng Aggregate trong một Bounded Context (2) cụ thể, thì pattern Repository có thể sẽ kém hữu dụng hơn. Nếu bạn đang truy xuất và sử dụng Entity (5) một cách trực tiếp và tùy tiện (ad hoc) thay vì thiết lập các ranh giới giao dịch Aggregate cẩn thận, có thể bạn sẽ thích tránh dùng Repository. Tuy nhiên, những người ít bận tâm đến các nguyên lý cốt lõi của DDD, chỉ áp dụng một số pattern của nó dưới góc độ thuần kỹ thuật, có thể sẽ chuộng Repository hơn Data Access Object. Một số người khác lại cho rằng việc trực tiếp sử dụng Session của cơ chế lưu trữ hoặc Unit of Work (đơn vị công việc quản lý giao dịch) [P of EAA] sẽ hợp lý hơn. Điều này không nhằm khuyên bạn nên tránh sử dụng Aggregate. Thực tế hoàn toàn ngược lại. Dù vậy, đây vẫn là một lựa chọn mà một số người sẽ áp dụng.

Theo đánh giá của tôi, có hai phong cách thiết kế Repository: thiết kế collection-oriented (hướng tập hợp) và thiết kế persistence-oriented (hướng lưu trữ bền vững). Có những trường hợp thiết kế hướng tập hợp sẽ phù hợp với bạn, và có những hoàn cảnh sử dụng thiết kế hướng lưu trữ bền vững mới là tốt nhất. Trước tiên, tôi sẽ bàn về thời điểm nên dùng và cách tạo một collection-oriented Repository, sau đó sẽ là phần xử lý cho các persistence-oriented Repository.

## Collection-Oriented Repository (Repository hướng tập hợp)

Chúng ta có thể coi thiết kế collection-oriented là một cách tiếp cận truyền thống bởi nó bám sát các ý tưởng nền tảng được trình bày trong pattern DDD nguyên bản. Thiết kế này bắt chước rất chặt chẽ một collection, mô phỏng lại ít nhất một phần interface tiêu chuẩn của nó. Tại đây, bạn thiết kế một interface Repository mà không để lộ bất kỳ dấu vết nào về cơ chế lưu trữ bên dưới, loại bỏ hoàn toàn các khái niệm như lưu (saving) hay ghi dữ liệu bền vững (persisting) vào kho lưu trữ.

Vì cách tiếp cận này đòi hỏi một số năng lực kỹ thuật đặc thù từ cơ chế lưu trữ nền tảng, nên có thể nó sẽ không phù hợp với hệ thống của bạn. Nếu cơ chế lưu trữ của bạn ngăn cản hoặc gây khó khăn cho việc thiết kế dưới góc nhìn collection, hãy xem tiểu mục tiếp theo. Tôi sẽ đề cập đến các điều kiện mà tôi cho rằng thiết kế hướng tập hợp hoạt động tối ưu nhất. Để làm được điều đó, tôi cần thiết lập một số kiến thức nền tảng.

Hãy xem cách hoạt động của một collection tiêu chuẩn. Trong Java, C# hay hầu hết các ngôn ngữ hướng đối tượng khác, các đối tượng được thêm vào collection và chúng sẽ nằm lại trong collection cho đến khi bị xóa đi. Bạn không cần phải làm bất cứ điều gì đặc biệt để collection nhận biết các thay đổi trên những đối tượng mà nó chứa, ngoại trừ việc yêu cầu collection cung cấp tham chiếu tới một đối tượng cụ thể, rồi sau đó yêu cầu chính đối tượng đó thực thi hành vi nào đó làm thay đổi trạng thái của nó. Bản thân đối tượng đó vẫn được collection nắm giữ, và giờ đây trạng thái của đối tượng bên trong đã khác so với trước khi sửa đổi.

Hãy xem xét kỹ hơn điều này thông qua một vài ví dụ. Lấy `java.util.Collection` làm ví dụ, dưới đây là một phần interface tiêu chuẩn của nó:

```java
package java.util;

public interface Collection ... {
    public boolean add(Object o);
    public boolean addAll(Collection c);
    public boolean remove(Object o);
    public boolean removeAll(Collection c);
    ...
}

```

Nếu muốn thêm một đối tượng vào collection, ta dùng add(). Nếu muốn xóa đối tượng đó, ta truyền tham chiếu của nó vào remove(). Bài test dưới đây giả định một collection vừa được khởi tạo thuộc loại nào đó có thể chứa các instance Calendar:

```java
assertTrue(calendarCollection.add(calendar));
assertEquals(1, calendarCollection.size());
assertTrue(calendarCollection.remove(calendar));
assertEquals(0, calendarCollection.size());

```

Khá đơn giản. Có một loại collection đặc biệt, `java.util.Set`, cùng lớp hiện thực `java.util.HashSet`, cung cấp đúng kiểu collection mà một Repository mô phỏng. Mọi đối tượng được thêm vào một Set phải là duy nhất. Nếu bạn cố thêm một đối tượng vốn đã tồn tại trong Set, nó sẽ không được thêm vào vì nó đã có sẵn. Vì vậy, bạn không bao giờ cần phải thêm cùng một đối tượng hai lần, như thể việc thêm lại lần nữa bằng cách nào đó sẽ lưu các thay đổi mà bạn đã yêu cầu đối tượng tự thực hiện. Các câu lệnh assertion trong bài test dưới đây chứng minh rằng việc thêm cùng một đối tượng nhiều hơn một lần không gây ra bất kỳ hiệu ứng nào, dù tích cực hay tiêu cực:

```java
Set<Calendar> calendarSet = new HashSet<Calendar>();

```

```java
assertTrue(calendarSet.add(calendar));
assertEquals(1, calendarSet.size());
assertFalse(calendarSet.add(calendar));
assertEquals(1, calendarSet.size());

```

Tất cả các assertion này đều vượt qua thành công bởi vì, mặc dù cùng một instance Calendar được thêm vào hai lần, lần cố gắng thêm thứ hai không hề làm thay đổi trạng thái của Set. Điều tương tự cũng áp dụng cho một Repository được thiết kế theo hướng tập hợp. Nếu chúng ta thêm instance Aggregate calendar vào một CalendarRepository được thiết kế theo hướng tập hợp, việc thêm calendar lần thứ hai là vô hại (benign). Mỗi Aggregate đều có một định danh duy nhất toàn cục gắn liền với Root Entity (gốc của cụm đối tượng) (5, 10). Chính định danh duy nhất này cho phép Repository hoạt động giống Set ngăn chặn việc thêm cùng một instance Aggregate nhiều hơn một lần.

Điều quan trọng là phải hiểu loại collection — một Set — mà Repository cần bắt chước. Bất kể triển khai phía sau bằng cơ chế lưu trữ cụ thể nào, bạn tuyệt đối không được phép để các instance của cùng một đối tượng bị thêm vào hai lần.

Một điểm mấu chốt khác là bạn không cần phải "lưu lại" (re-save) các đối tượng đã được sửa đổi vốn đã được Repository quản lý. Hãy nghĩ lại cách bạn sửa đổi một đối tượng đang nằm trong collection. Thực ra nó rất đơn giản. Bạn chỉ cần lấy tham chiếu của đối tượng bạn muốn sửa đổi từ collection ra, sau đó yêu cầu đối tượng thực thi một hành vi chuyển đổi trạng thái bằng cách gọi một command method.

## Điểm cốt lõi của Collection-Oriented Repository (Take-aways for Collection-Oriented Repositories)

Một Repository nên bắt chước một collection dạng Set. Bất kể giải pháp triển khai bên dưới bằng cơ chế lưu trữ nào, bạn không được phép để các instance của cùng một đối tượng bị thêm hai lần. Đồng thời, khi lấy các đối tượng từ Repository ra và chỉnh sửa chúng, bạn không cần phải "lưu lại" chúng vào Repository.

Để minh họa, giả sử chúng ta mở rộng (subclass) một lớp tiêu chuẩn `java.util.HashSet` và tạo một phương thức trên kiểu mới này cho phép chúng ta tìm kiếm một instance đối tượng cụ thể dựa vào định danh duy nhất. Chúng ta sẽ đặt cho lớp kế thừa này một cái tên xác định nó là một Repository, nhưng bản chất nó chỉ là một HashSet trong bộ nhớ:

```java
public class CalendarRepository extends HashSet {
    private Set<CalendarId, Calendar> calendars;

```

## COLLECTION-ORIENTED REPOSITORIES

```java
    public CalendarRepository() {
        this.calendars = new HashSet<CalendarId, Calendar>();
    }

    public void add(Calendar aCalendar) {
        this.calendars.add(aCalendar.calendarId(), aCalendar);
    }

    public Calendar findCalendar(CalendarId aCalendarId) {
        return this.calendars.get(aCalendarId);
    }
}

```

Bình thường chúng ta không kế thừa HashSet để tạo một Repository điển hình. Ở đây chúng tôi làm vậy chỉ nhằm mục đích lấy ví dụ. Quay lại ví dụ trên: bây giờ chúng ta có thể thêm một instance Calendar vào Set chuyên biệt này, sau đó tìm lại instance đó và yêu cầu nó tự sửa đổi:

```java
CalendarId calendarId = new CalendarId(...);
Calendar calendar = new Calendar(calendarId, "Project Calendar", ...);
CalendarRepository calendarRepository = new CalendarRepository();

calendarRepository.add(calendar);

// sau đó ...
Calendar calendarToRename = calendarRepository.findCalendar(calendarId);
calendarToRename.rename("CollabOvation Project Calendar");

// sau đó nữa ...
Calendar calendarThatWasRenamed = calendarRepository.findCalendar(calendarId);
assertEquals("CollabOvation Project Calendar", calendarThatWasRenamed.name());

```

Lưu ý rằng instance của Calendar, được tham chiếu bởi calendarToRename, được sửa đổi bằng cách yêu cầu nó tự đổi tên. Rất lâu sau đó, sau khi tác vụ đổi tên hoàn tất, tên của nó vẫn giữ đúng giá trị đã được thay đổi. Điều này đạt được mà không cần phải yêu cầu lớp con của HashSet là CalendarRepository lưu các thay đổi cho instance Calendar — việc làm vốn dĩ hoàn toàn vô nghĩa. CalendarRepository không hề có phương thức save() vì không có nhu cầu đó. Không có lý do gì phải lưu các thay đổi của instance Calendar mà calendarToRename tham chiếu tới, bởi vì collection vẫn đang giữ tham chiếu đến đối tượng bị sửa đổi, và các sửa đổi được thực hiện trực tiếp trên chính đối tượng đó.

Điểm mấu chốt ở đây là: một collection-oriented Repository truyền thống thực sự bắt chước một collection ở chỗ không có bất kỳ thành phần nào của cơ chế lưu trữ bị lộ ra ngoài cho client thông qua public interface. Do đó, mục tiêu của chúng ta là thiết kế và triển khai một collection-oriented Repository mang đầy đủ các đặc tính được thể hiện bởi một HashSet, nhưng thay vào đó lại kết nối tới một kho lưu trữ dữ liệu bền vững.

Như bạn có thể hình dung, điều này đòi hỏi một số năng lực đặc thù từ cơ chế lưu trữ phía sau. Cơ chế lưu trữ phải hỗ trợ khả năng theo dõi ngầm (implicitly track) các thay đổi được thực hiện trên từng đối tượng bền vững mà nó quản lý theo một cách nào đó. Điều này có thể được thực hiện thông qua nhiều giải pháp khác nhau, bao gồm hai phương pháp sau:

1. Implicit Copy-on-Read (sao chép ngầm khi đọc) [Keith & Stafford]: Cơ chế lưu trữ sẽ tự động sao chép ngầm từng đối tượng lưu trữ khi đọc tại thời điểm nó được tái tạo từ kho dữ liệu, sau đó so sánh bản sao nội bộ này với bản sao của client lúc commit giao dịch. Đi sâu vào chi tiết: khi bạn yêu cầu cơ chế lưu trữ đọc một đối tượng từ kho dữ liệu, nó sẽ thực thi và ngay lập tức tạo một bản sao toàn bộ đối tượng (trừ các phần nạp lười - lazy-loaded, vốn có thể được nạp và sao chép sau). Khi giao dịch tạo ra thông qua cơ chế lưu trữ được commit, cơ chế này sẽ kiểm tra các sửa đổi trên các đối tượng đã nạp (hoặc gắn lại - reattached) bằng cách so sánh chúng với bản sao. Mọi đối tượng phát hiện có thay đổi sẽ được flush (đồng bộ đẩy dữ liệu) xuống kho dữ liệu.
2. Implicit Copy-on-Write (sao chép ngầm khi ghi) [Keith & Stafford]: Cơ chế lưu trữ quản lý tất cả các đối tượng lưu trữ đã nạp thông qua một proxy (đối tượng ủy nhiệm). Khi mỗi đối tượng được nạp từ kho dữ liệu, một proxy mỏng được tạo ra và trao cho client. Client sẽ gọi hành vi trên đối tượng proxy mà không hề hay biết, và proxy sẽ chuyển tiếp hành vi đó sang đối tượng thực. Khi proxy nhận lệnh gọi phương thức lần đầu tiên, nó sẽ tạo một bản sao của đối tượng được quản lý. Proxy theo dõi các thay đổi được thực hiện trên trạng thái của đối tượng được quản lý và đánh dấu nó là dirty (đã bị thay đổi). Khi giao dịch tạo qua cơ chế lưu trữ được commit, nó sẽ kiểm tra các đối tượng dirty và toàn bộ các đối tượng đó sẽ được flush xuống kho dữ liệu.

Ưu điểm và sự khác biệt giữa các phương pháp này có thể khác nhau, và nếu hệ thống của bạn có nguy cơ chịu ảnh hưởng tiêu cực từ việc chọn sai phương pháp, bạn cần cân nhắc đo lường chúng cẩn thận. Dĩ nhiên, bạn có thể quyết định chọn công cụ mình thích thay vì tìm hiểu kỹ lưỡng, nhưng đó có thể không phải là quyết định an toàn nhất.

Tuy vậy, ưu điểm tổng thể của cả hai cách tiếp cận này là các thay đổi trên đối tượng bền vững được theo dõi một cách ngầm định, không đòi hỏi client phải biết hay can thiệp tường minh để báo cho cơ chế lưu trữ biết về thay đổi. Điểm cốt lõi ở đây là: việc sử dụng một cơ chế lưu trữ như vậy, chẳng hạn như Hibernate, cho phép bạn áp dụng mô hình collection-oriented Repository truyền thống.

Mặc dù vậy, ngay cả khi bạn có quyền tự do sử dụng một cơ chế lưu trữ có khả năng theo dõi thay đổi thông qua sao chép ngầm như Hibernate, đôi khi việc sử dụng nó lại không mong muốn hoặc không phù hợp. Nếu yêu cầu hệ thống đòi hỏi một domain có hiệu năng cực cao với rất nhiều đối tượng nằm trong bộ nhớ tại bất kỳ thời điểm nào, cơ chế kiểu này sẽ tạo ra overhead (chi phí phụ trội) không đáng có, cả về bộ nhớ lẫn tốc độ thực thi. Bạn sẽ phải cân nhắc và quyết định cẩn thận xem liệu nó có phù hợp với mình hay không. Chắc chắn có rất nhiều domain mà Hibernate hoạt động rất hiệu quả. Vì vậy đừng coi lời cảnh báo của tôi như một nỗ lực nhằm cấm đoán công nghệ này. Việc sử dụng bất kỳ công cụ nào cũng phải đi kèm với nhận thức đầy đủ về các đánh đổi (trade-offs).

## Triết lý cao bồi (Cowboy Logic)

LB: "Khi con chó của tôi bị nhiễm giun, bác sĩ thú y đã kê cho nó vài cái repository."

> 💡 **Giải thích thêm:** Đây là một câu chơi chữ (pun) bắt nguồn từ sự phát âm gần giống nhau trong tiếng Anh giữa "repository" (kho lưu trữ) và "suppository" (thuốc đặt hậu môn / thuốc đạn — dạng thuốc thú y thường dùng để trị bệnh đường ruột/giun sán cho vật nuôi). Người nói đã nghe nhầm chỉ định "suppositories" của bác sĩ thành "repositories". Tác giả lồng ghép mẩu chuyện vui dân gian này để chuyển tiếp sang chủ đề công cụ kỹ thuật kế tiếp.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Điều này có thể khiến bạn cân nhắc việc sử dụng một công cụ ánh xạ đối tượng - quan hệ (ORM) có hiệu năng tối ưu hơn, có khả năng hỗ trợ một collection-oriented Repository. Một trong những công cụ như vậy là TopLink của Oracle, cùng người anh em gần gũi nhất của nó là EclipseLink. TopLink cung cấp một Unit of Work, vốn không hoàn toàn khác biệt so với Session của Hibernate. Tuy nhiên, Unit of Work của TopLink không thực hiện sao chép ngầm khi đọc (implicit copy-on-read). Thay vào đó, nó sử dụng Explicit Copy-before-Write (sao chép tường minh trước khi ghi) [Keith & Stafford]. Ở đây, thuật ngữ "tường minh" (explicit) có nghĩa là client phải thông báo cho Unit of Work biết rằng các thay đổi sắp diễn ra. Điều này mang lại cho Unit of Work cơ hội nhân bản (clone) đối tượng domain được chỉ định để chuẩn bị cho việc sửa đổi (những gì nó gọi là edits, sẽ thảo luận sau trong chương này). Điểm mấu chốt là TopLink chỉ tiêu tốn bộ nhớ khi thực sự bắt buộc.

## Hiện thực hóa với Hibernate (Hibernate Implementation)

Có hai bước chính để tạo Repository theo bất kỳ định hướng nào. Bạn cần định nghĩa một public interface và ít nhất một lớp triển khai (implementation).

Cụ thể trong trường hợp thiết kế hướng tập hợp, ở bước đầu tiên bạn định nghĩa một interface mô phỏng một collection. Bước thứ hai cung cấp một lớp triển khai giải quyết việc sử dụng cơ chế lưu trữ chính bên dưới, chẳng hạn như Hibernate. Giống như một collection, interface sẽ thường có các phương thức phổ biến như trong ví dụ sau:

```java
package com.saasovation.collaboration.domain.model.calendar;

public interface CalendarEntryRepository {
    public void add(CalendarEntry aCalendarEntry);
    public void addAll(Collection<CalendarEntry> aCalendarEntryCollection);
    public void remove(CalendarEntry aCalendarEntry);
    public void removeAll(Collection<CalendarEntry> aCalendarEntryCollection);
    ...
}

```

Hãy đặt định nghĩa interface trong cùng Module (9) với kiểu Aggregate mà nó lưu trữ. Trong trường hợp này, interface CalendarEntryRepository được đặt trong cùng Module (Java package) với CalendarEntry. Lớp triển khai sẽ nằm trong một package riêng biệt, như sẽ thảo luận ở phần sau.

Interface CalendarEntryRepository có các phương thức rất giống với các phương thức do các collection cung cấp, chẳng hạn như `java.util.Collection` tiêu chuẩn. Một CalendarEntry mới có thể được thêm vào Repository này bằng `add()`. Nhiều instance mới có thể được thêm vào bằng `addAll()`. Khi các instance đã được thêm vào, chúng sẽ được lưu bền vững vào một kho dữ liệu nào đó và có thể truy xuất lại bằng định danh duy nhất kể từ thời điểm đó. Ngược lại với các phương thức trên là `remove()` và `removeAll()`, cho phép xóa một hoặc nhiều instance khỏi collection.

Cá nhân tôi không thích các phương thức này trả về kết quả kiểu Boolean như các collection hoàn chỉnh. Đó là bởi vì trong một số trường hợp, việc trả về true cho một thao tác dạng thêm mới không đảm bảo sự thành công. Kết quả true vẫn có thể phụ thuộc vào việc commit giao dịch trên kho dữ liệu sau đó. Do đó, void có thể là kiểu trả về chính xác hơn đối với trường hợp của một Repository.

Có thể có những trường hợp việc thêm và/hoặc xóa nhiều instance Aggregate trong một giao dịch là không phù hợp. Khi điều đó đúng với một trường hợp cụ thể trong miền của bạn, đừng đưa các phương thức `addAll()` và `removeAll()` vào. Tuy nhiên, các phương thức này chỉ được cung cấp để tạo sự thuận tiện. Client luôn có thể sử dụng vòng lặp để gọi `add()` hoặc `remove()` nhiều lần khi tự mình duyệt qua một collection. Do đó, việc loại bỏ các phương thức `addAll()` và `removeAll()` chỉ mang tính tượng trưng cho một chính sách vốn dĩ không thể thực sự ép buộc bằng thiết kế, trừ khi bạn xây dựng thêm cơ chế phát hiện việc thêm và xóa nhiều đối tượng trong một giao dịch đơn lẻ. Việc làm này nhiều khả năng sẽ yêu cầu Repository phải được khởi tạo cho mỗi giao dịch — một đề xuất có chi phí tiềm ẩn khá lớn. Tôi sẽ không thảo luận thêm về điều này.

Có khả năng các instance của một số kiểu Aggregate không bao giờ được phép xóa thông qua các luồng use case thông thường của ứng dụng. Có thể cần phải giữ lại (retain) instance này rất lâu sau khi nó không còn dùng được trong ứng dụng nữa, có thể vì mục đích tham chiếu và/hoặc lịch sử. Về mặt quan hệ tham chiếu, việc xóa một số đối tượng thực tế có thể rất khó hoặc bất khả thi. Xét theo góc độ nghiệp vụ, việc xóa một số đối tượng có thể là không khôn ngoan, thiếu cân nhắc, hoặc thậm chí là phạm pháp. Trong những trường hợp đó, bạn có thể quyết định đơn giản là đánh dấu instance Aggregate đó là vô hiệu hóa (disabled), không sử dụng được (unusable), hoặc bị xóa logic (logically removed) theo một cách đặc thù nào đó của miền nghiệp vụ. Nếu vậy, bạn có thể quyết định không đưa bất kỳ phương thức xóa nào vào public interface của Repository, hoặc bạn có thể chọn triển khai các phương thức xóa đó để thiết lập trạng thái không thể sử dụng cho instance Aggregate. Bạn cũng có thể ngăn chặn việc xóa đối tượng hoàn toàn thông qua code review, nơi các đoạn mã client được kiểm tra kỹ lưỡng để đảm bảo không tồn tại bất kỳ hành vi xóa nào như vậy. Đây là một quyết định cần cân nhắc, nhưng bạn có thể thấy việc cấm hẳn thao tác xóa sẽ dễ dàng hơn nhiều. Xét cho cùng, bất kỳ phương thức nào trên public interface nhìn chung đều được coi là sẵn sàng để sử dụng. Nếu tính năng xóa được mở công khai trong khi về mặt logic lại bị cấm, có lẽ bạn nên cân nhắc triển khai xóa logic thay vì xóa vật lý.

Một phần quan trọng khác của interface Repository là định nghĩa các finder method (phương thức tìm kiếm):

```java
public interface CalendarEntryRepository {
    ...
    public CalendarEntry calendarEntryOfId(
        Tenant aTenant,
        CalendarEntryId aCalendarEntryId);

    public Collection<CalendarEntry> calendarEntriesOfCalendar(
        Tenant aTenant,
        CalendarId aCalendarId);

    public Collection<CalendarEntry> overlappingCalendarEntries(
        Tenant aTenant,
        CalendarId aCalendarId,
        TimeSpan aTimeSpan);
}

```

Định nghĩa phương thức đầu tiên, `calendarEntryOfId()`, cho phép bạn truy xuất một instance cụ thể của Aggregate CalendarEntry theo định danh duy nhất. Kiểu này sử dụng một kiểu định danh tường minh, cụ thể là CalendarEntryId. Định nghĩa phương thức thứ hai, `calendarEntriesOfCalendar()`, cho phép bạn truy xuất một collection gồm tất cả các instance CalendarEntry của một Calendar cụ thể dựa theo định danh duy nhất của nó. Cuối cùng, định nghĩa phương thức tìm kiếm thứ ba, `overlappingCalendarEntries()`, cung cấp một collection chứa tất cả các instance CalendarEntry cho một Calendar cụ thể nằm trong một khoảng thời gian TimeSpan xác định. Cụ thể, phương thức này hỗ trợ truy xuất các mục đã được lên lịch trong một khoảng thời gian và ngày tháng liên tục xác định.

Cuối cùng, bạn có thể tự hỏi làm thế nào một CalendarEntry được gán định danh duy nhất toàn cục. Điều này cũng có thể được Repository cung cấp một cách tiện lợi:

```java
public interface CalendarEntryRepository {
    public CalendarEntryId nextIdentity();
    ...
}

```

Bất kỳ đoạn code nào chịu trách nhiệm khởi tạo các instance CalendarEntry mới đều sử dụng `nextIdentity()` để nhận về một instance CalendarEntryId mới:

```java
CalendarEntry calendarEntry = new CalendarEntry(
    tenant,
    calendarId,
    calendarEntryRepository.nextIdentity(),
    owner,
    subject,
    description,
    timeSpan,
    alarm,
    repetition,
    location,
    invitees);

```

Xem Chương 5: Entities để biết thảo luận chi tiết về các kỹ thuật tạo định danh, việc sử dụng định danh đặc thù miền nghiệp vụ (domain-specific identity) và định danh thay thế (surrogate identity), cũng như tầm quan trọng của việc chọn đúng thời điểm gán định danh.

Bây giờ chúng ta hãy xem xét lớp triển khai cho Repository truyền thống này. Có một vài lựa chọn về Module để đặt lớp này. Một số người thích sử dụng Module (Java package) nằm ngay bên dưới Module chứa Aggregate và Repository. Trong trường hợp này, điều đó có nghĩa là:

```java
package com.saasovation.collaboration.domain.model.calendar.impl;

public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    ...
}

```

Đặt lớp ở đây cho phép bạn quản lý việc triển khai trong Domain Layer, nhưng nằm trong một package đặc biệt dành cho các implementation. Bằng cách đó, bạn giữ cho các khái niệm nghiệp vụ tách biệt hoàn toàn khỏi các phần trực tiếp xử lý lưu trữ dữ liệu. Phong cách khai báo interface trong một package có tên giàu ý nghĩa nghiệp vụ và các implementation của chúng trong một sub-package có tên `impl` nằm ngay dưới đó được áp dụng rộng rãi trong các dự án Java. Tuy nhiên, trong trường hợp của Collaboration Context, nhóm phát triển đã chọn đặt tất cả các lớp triển khai kỹ thuật vào Infrastructure Layer:

```java
package com.saasovation.collaboration.infrastructure.persistence;

public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    ...
}

```

Cách này sử dụng Dependency Inversion Principle (DIP - nguyên lý đảo ngược phụ thuộc) (4) để phân tầng các mối bận tâm về hạ tầng kỹ thuật. Infrastructure Layer đứng ở vị trí cao hơn về mặt logic so với tất cả các tầng khác, giúp các tham chiếu trở thành đơn hướng và trỏ xuống Domain Layer.

Lớp HibernateCalendarEntryRepository là một Spring bean đã được đăng ký. Nó có một constructor không đối số và được dependency inject một bean đối tượng hạ tầng khác:

```java
import com.saasovation.collaboration.infrastructure.persistence.SpringHibernateSessionProvider;

public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    public HibernateCalendarEntryRepository() {
        super();
    }
    ...
    private SpringHibernateSessionProvider sessionProvider;

    public void setSessionProvider(SpringHibernateSessionProvider aSessionProvider) {
        this.sessionProvider = aSessionProvider;
    }

    private org.hibernate.Session session() {
        return this.sessionProvider.session();
    }
}

```

Lớp SpringHibernateSessionProvider cũng được đặt trong Infrastructure Layer thuộc Module `com.saasovation.collaboration.infrastructure.persistence` và được inject vào từng Repository dựa trên Hibernate. Mỗi phương thức sử dụng đối tượng Session của Hibernate sẽ tự gọi phương thức `session()` để lấy nó. Phương thức `session()` sử dụng instance `sessionProvider` được inject để lấy instance Session gắn với luồng hiện tại (thread-bound Session, sẽ được trình bày sau trong chương này).

Các phương thức `add()`, `addAll()`, `remove()` và `removeAll()` được triển khai như sau:

```java
package com.saasovation.collaboration.infrastructure.persistence;

public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    ...
    @Override
    public void add(CalendarEntry aCalendarEntry) {
        try {
            this.session().saveOrUpdate(aCalendarEntry);
        } catch (ConstraintViolationException e) {
            throw new IllegalStateException("CalendarEntry is not unique.", e);
        }
    }

    @Override
    public void addAll(Collection<CalendarEntry> aCalendarEntryCollection) {
        try {
            for (CalendarEntry instance : aCalendarEntryCollection) {
                this.session().saveOrUpdate(instance);
            }
        } catch (ConstraintViolationException e) {
            throw new IllegalStateException("CalendarEntry is not unique.", e);
        }
    }

    @Override
    public void remove(CalendarEntry aCalendarEntry) {
        this.session().delete(aCalendarEntry);
    }

    @Override
    public void removeAll(Collection<CalendarEntry> aCalendarEntryCollection) {
        for (CalendarEntry instance : aCalendarEntryCollection) {
            this.session().delete(instance);
        }
    }
    ...
}

```

Các phương thức này có phần triển khai khá tinh gọn. Mỗi phương thức tự gọi `session()` để lấy instance Hibernate Session (như vừa giải thích ở trên).

Có thể bạn sẽ thấy lạ khi các phương thức `add()` và `addAll()` lại sử dụng phương thức `saveOrUpdate()` của Session. Điều này nhằm hỗ trợ thêm cho thao tác thêm mới dạng Set. Nếu một client tình cờ thêm cùng một CalendarEntry nhiều hơn một lần, hành vi của `saveOrUpdate()` sẽ khiến nó trở thành một no-op (thao tác không thực thi gì) vô hại. Trên thực tế, kể từ Hibernate phiên bản 3, bất kỳ hình thức cập nhật nào cũng là no-op vì như đã lưu ý trước đó, các cập nhật được theo dõi ngầm thông qua việc sửa đổi trạng thái đối tượng. Do đó, trừ khi các đối tượng được thêm bởi hai phương thức này là hoàn toàn mới, hành vi này sẽ không làm gì cả.

Thao tác thêm có thể gây ra ngoại lệ `ConstraintViolationException`. Thay vì để các exception của Hibernate tràn ra phía client, những exception đó được bắt lại và bọc bên trong ngoại lệ `IllegalStateException` thân thiện hơn với client. Chúng ta cũng có thể khai báo các exception đặc thù miền nghiệp vụ và ném chúng ra ngoài. Đó là sự lựa chọn của từng nhóm dự án. Điểm quan trọng là một khi đã tốn công trừu tượng hóa các chi tiết triển khai của framework lưu trữ bên dưới, chúng ta muốn cách ly client khỏi toàn bộ các chi tiết đó, bao gồm cả các exception.

Các phương thức `remove()` và `removeAll()` khá đơn giản. Chúng chỉ cần sử dụng `delete()` của Session để hỗ trợ xóa khỏi kho dữ liệu bên dưới. Có một chi tiết bổ sung liên quan đến việc xóa các Aggregate sử dụng quan hệ ánh xạ một-một (one-to-one), vốn xuất hiện trong một trường hợp ở Identity and Access Context. Vì bạn không thể cascade (xóa lan truyền) các thay đổi trên những mối quan hệ như vậy, bạn sẽ cần phải xóa tường minh các đối tượng ở cả hai đầu của mối liên kết:

```java
package com.saasovation.identityaccess.infrastructure.persistence;

public class HibernateUserRepository implements UserRepository {
    ...
    @Override
    public void remove(User aUser) {
        this.session().delete(aUser.person());
        this.session().delete(aUser);
    }

    @Override
    public void removeAll(Collection<User> aUserCollection) {
        for (User instance : aUserCollection) {
            this.session().delete(instance.person());
            this.session().delete(instance);
        }
    }
    ...
}

```

Đối tượng Person bên trong phải bị xóa trước, sau đó mới đến Aggregate Root User. Nếu bạn không xóa đối tượng Person bên trong, nó sẽ bị mồ côi (orphaned) trong bảng cơ sở dữ liệu tương ứng. Nhìn chung, đây là lý do chính đáng để tránh các liên kết một-một và thay vào đó nên sử dụng liên kết đơn hướng nhiều-một có ràng buộc (constrained singular many-to-one unidirectional association). Tuy nhiên, tôi đã cố tình chọn triển khai liên kết hai chiều một-một nhằm minh họa những gì phát sinh khi phải làm việc với các kiểu ánh xạ rắc rối hơn.

Lưu ý rằng có nhiều cách tiếp cận ưu tiên khác nhau để xử lý các tình huống như vậy. Một số người có thể chọn dựa vào các lifecycle event của ORM để kích hoạt việc xóa lan truyền đối tượng thành phần. Tôi đã chủ ý tránh các cách tiếp cận như vậy vì tôi phản đối mạnh mẽ việc để Aggregate tự quản lý lưu trữ (Aggregate-managed persistence), và tôi ủng hộ mạnh mẽ việc chỉ để Repository quản lý lưu trữ (Repository-only persistence). Các cuộc tranh luận xoay quanh vấn đề này luôn gay gắt và kéo dài bất tận. Bạn nên đưa ra lựa chọn sáng suốt, nhưng hãy hiểu rằng các chuyên gia DDD luôn tránh việc lưu trữ do Aggregate tự quản lý như một nguyên tắc nằm lòng.

Bây giờ quay trở lại với HibernateCalendarEntryRepository và phần triển khai các phương thức finder của nó:

```java
public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    ...
    @Override
    @SuppressWarnings("unchecked")
    public Collection<CalendarEntry> overlappingCalendarEntries(
        Tenant aTenant,
        CalendarId aCalendarId,
        TimeSpan aTimeSpan) {

        Query query = this.session().createQuery(
            "from CalendarEntry as _obj_ " +
            "where _obj_.tenant = :tenant and " +
            "_obj_.calendarId = :calendarId and " +
            "((_obj_.repetition.timeSpan.begins between " +
            ":tsb and :tse) or " +
            " (_obj_.repetition.timeSpan.ends between " +
            ":tsb and :tse))");

        query.setParameter("tenant", aTenant);
        query.setParameter("calendarId", aCalendarId);
        query.setParameter("tsb", aTimeSpan.begins(), Hibernate.DATE);
        query.setParameter("tse", aTimeSpan.ends(), Hibernate.DATE);

        return (Collection<CalendarEntry>) query.list();
    }

    @Override
    public CalendarEntry calendarEntryOfId(
        Tenant aTenant,
        CalendarEntryId aCalendarEntryId) {

        Query query = this.session().createQuery(
            "from CalendarEntry as _obj_ " +
            "where _obj_.tenant = ? and _obj_.calendarEntryId = ?");

```

```java
        query.setParameter(0, aTenant);
        query.setParameter(1, aCalendarEntryId);

        return (CalendarEntry) query.uniqueResult();
    }

    @Override
    @SuppressWarnings("unchecked")
    public Collection<CalendarEntry> calendarEntriesOfCalendar(
        Tenant aTenant,
        CalendarId aCalendarId) {

        Query query = this.session().createQuery(
            "from CalendarEntry as _obj_ " +
            "where _obj_.tenant = ? and _obj_.calendarId = ?");

        query.setParameter(0, aTenant);
        query.setParameter(1, aCalendarId);

        return (Collection<CalendarEntry>) query.list();
    }
    ...
}

```

Mỗi phương thức trong số ba finder đều tạo một Query thông qua Session của nó. Theo thông lệ với các truy vấn Hibernate, nhóm phát triển sử dụng HQL (Hibernate Query Language - ngôn ngữ truy vấn của Hibernate) để mô tả các tiêu chí và sau đó nạp các đối tượng tham số vào. Truy vấn sau đó được chạy, yêu cầu trả về một kết quả đơn lẻ duy nhất hoặc một collection danh sách các đối tượng. Phức tạp hơn cả trong ba truy vấn là `overlappingCalendarEntries()`, trong đó chúng ta phải tìm tất cả các instance CalendarEntry bị trùng lặp trong một khoảng ngày giờ cụ thể, tức TimeSpan.

Cuối cùng, chúng ta xem xét phần triển khai của phương thức `nextIdentity()`:

```java
public class HibernateCalendarEntryRepository implements CalendarEntryRepository {
    ...
    public CalendarEntryId nextIdentity() {
        return new CalendarEntryId(
            UUID.randomUUID().toString().toUpperCase());
    }
    ...
}

```

Cách triển khai cụ thể này không sử dụng cơ chế lưu trữ hay kho dữ liệu để sinh ra định danh duy nhất. Thay vào đó, nó sử dụng bộ tạo UUID tương đối nhanh và rất đáng tin cậy.

## Các cân nhắc khi hiện thực hóa với TopLink (Considerations for a TopLink Implementation)

TopLink sở hữu cả Session lẫn Unit of Work. Điều này có phần khác biệt so với Hibernate ở chỗ Session của Hibernate đồng thời cũng là một Unit of Work. 1 Hãy cùng xem xét góc nhìn về việc sử dụng Unit of Work tách biệt khỏi Session, sau đó dần chuyển sang cách ứng dụng chúng vào một lớp triển khai Repository.

Nếu không có sự hỗ trợ của lớp trừu tượng Repository, bạn sẽ phải sử dụng TopLink theo cách sau:

```java
Calendar calendar = session.readObject(...);
UnitOfWork unitOfWork = session.acquireUnitOfWork();
Calendar calendarToRename = unitOfWork.registerObject(calendar);
calendarToRename.rename("CollabOvation Project Calendar");
unitOfWork.commit();

```

UnitOfWork giúp tối ưu hóa việc sử dụng bộ nhớ và năng lực xử lý hiệu quả hơn nhiều, bởi vì bạn phải thông báo tường minh cho UnitOfWork biết rằng bạn có ý định sửa đổi đối tượng. Chỉ đến thời điểm đó, một bản clone (bản sao phục vụ chỉnh sửa) của Aggregate mới được tạo ra. Như đã trình bày ở trên, phương thức `registerObject()` trả về một bản clone của instance Calendar gốc. Chính đối tượng clone này, được tham chiếu bởi `calendarToRename`, mới là đối tượng cần được chỉnh sửa/thay đổi. Khi bạn thực hiện các sửa đổi trên đối tượng, TopLink có khả năng theo dõi các thay đổi diễn ra. Khi phương thức `commit()` trên UnitOfWork được gọi, tất cả các đối tượng đã sửa đổi sẽ được commit vào cơ sở dữ liệu. 2

Việc thêm đối tượng mới vào một TopLink Repository có thể được thực hiện khá dễ dàng:

```java
...
public void add(Calendar aCalendar) {
    this.unitOfWork().registerNewObject(aCalendar);
}
...

```

1. Tôi không đánh giá giá trị của TopLink dựa trên tiêu chuẩn của Hibernate. Trên thực tế, TopLink có một lịch sử thành công lâu đời, được thiết lập từ rất lâu trước khi Oracle mua lại sản phẩm này sau sự sụp đổ của WebGain và đợt "bán tống bán tháo" sau đó. TOP là từ viết tắt của "The Object People" — công ty ban đầu đứng sau công cụ này với gần hai thập kỷ thành công đã được chứng minh. Ở đây tôi chỉ đơn thuần so sánh sự khác biệt trong cách thức vận hành của hai công cụ.
2. Điều này giả định rằng Unit of Work không bị lồng bên trong một Unit of Work cha. Nếu nó nằm lồng trong một Unit of Work cha, các thay đổi từ Unit of Work được commit sẽ được hợp nhất (merge) vào cha của nó. Cuối cùng, Unit of Work ngoài cùng mới là đối tượng commit dữ liệu vào database.

Việc sử dụng `registerNewObject()` quy định rằng `aCalendar` là một instance mới. Điều này sẽ bắt buộc phát sinh lỗi nếu `add()` được gọi với một `aCalendar` vốn đã tồn tại từ trước. Chúng ta cũng có thể sử dụng phương thức `registerObject()` thông thường ở đây, cách này sẽ tương tự như việc sử dụng phương thức `saveOrUpdate()` của Hibernate (đã thảo luận trước đó). Dù bằng cách nào, chúng ta cũng đáp ứng được nhu cầu về một interface hướng tập hợp có khả năng hoạt động tốt.

Nhưng chúng ta vẫn cần một cách để lấy được bản clone khi cần sửa đổi một Aggregate đã tồn tại từ trước. Bí quyết là tìm ra một giải pháp thuận tiện để đăng ký instance Aggregate đó với một UnitOfWork. Cho đến nay, cuộc thảo luận của chúng ta vẫn chưa đưa ra một interface Repository nào làm được điều đó, bởi vì chúng ta đang cố gắng bắt chước một Set và tránh bất kỳ sự suy diễn nào về việc lưu trữ dữ liệu xuất hiện trên interface. Mặc dù vậy, chúng ta vẫn có thể hoàn thành việc này theo cách không nhất thiết phải làm lộ ra tư duy về mặt lưu trữ bền vững. Hãy cân nhắc áp dụng một trong hai cách tiếp cận sau:

```java
public Calendar editingCopy(Calendar aCalendar);
// hoặc
public void useEditingMode();

```

Với cách tiếp cận thứ nhất, `editingCopy()` sẽ lấy về một UnitOfWork, đăng ký instance Calendar đã cho, nhận lấy bản clone của nó và trả về:

```java
...
public Calendar editingCopy(Calendar aCalendar) {
    return (Calendar) this.unitOfWork().registerObject(aCalendar);
}
...

```

Cách này phản ánh cách thức hoạt động của phương thức `registerObject()` bên dưới. Dễ hiểu là điều này có thể không thực sự lý tưởng, nhưng đây là một cách tiếp cận rõ ràng và không mang nặng tư duy về việc lưu trữ dữ liệu.

Cách tiếp cận thứ hai là đưa Repository vào chế độ chỉnh sửa thông qua `useEditingMode()`. Sau khi thực hiện thao tác này, tất cả các finder method tiếp theo sẽ tự động đăng ký mọi đối tượng mà chúng truy vấn với một UnitOfWork phía sau và trả về các bản clone. Về cơ bản, điều này sẽ khóa Repository vào mục đích phục vụ cho các sửa đổi Aggregate. Dù sao đi nữa, đó cũng chính là cách thức Repository thường được sử dụng: hoặc là chỉ đọc (read-only), hoặc là đọc để sửa đổi. Nó cũng phản ánh việc sử dụng Repository cho các Aggregate vốn có các ranh giới được thiết kế chuẩn xác, hướng tới sự thành công của các giao dịch.

Có thể có những cách khác để thiết kế một collection-oriented repository cho TopLink, nhưng những giải pháp trên cung cấp một vài lựa chọn rất đáng để cân nhắc.