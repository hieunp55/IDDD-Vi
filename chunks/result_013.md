Một số nhà phát triển gọi các loại kiểm tra tiền điều kiện (precondition check) này là lập trình phòng thủ (defensive programming). Việc dựng rào chắn để ngăn chặn các giá trị hoàn toàn không hợp lệ xâm nhập vào mô hình của bạn chắc chắn là lập trình phòng thủ. Tuy nhiên, một số người có thể không đồng tình với mức độ chi tiết ngày càng tăng của các chốt chặn này. Một vài lập trình viên theo trường phái phòng thủ đồng ý với việc kiểm tra giá trị rỗng (null), thậm chí kiểm tra chuỗi rỗng (empty string), nhưng lại e ngại việc kiểm tra các điều kiện như độ dài chuỗi, khoảng giá trị số, định dạng dữ liệu và những thứ tương tự. Chẳng hạn, một số người cho rằng việc phó mặc việc kiểm tra kích thước giá trị cho cơ sở dữ liệu là cách tốt nhất. Họ coi những việc như giới hạn độ dài tối đa của chuỗi là mối bận tâm của một thành phần nào đó ngoài các đối tượng mô hình. Dẫu vậy, các tiền điều kiện này hoàn toàn có thể được xem là các bước kiểm tra tính hợp lý (sanity check) hết sức chính đáng.

Có thể có những trường hợp việc kiểm tra độ dài chuỗi là không cần thiết. Điều này có thể hợp lý khi sử dụng một cơ sở dữ liệu mà kích thước tối đa của cột `NVARCHAR` không bao giờ bị chạm tới. Các cột văn bản của Microsoft SQL Server có thể được khai báo bằng từ khóa `max`:

```sql
CREATE TABLE PERSON (
    ...
    CONTACT_INFORMATION_EMAIL_ADDRESS_ADDRESS NVARCHAR(max) NOT NULL,
    ...
) ON PRIMARY
GO

```

Vấn đề không phải là chúng ta mong muốn một địa chỉ email dài tới 1.073.741.822 ký tự. Đơn giản là chúng ta muốn khai báo một độ rộng cột mà bản thân sẽ không bao giờ phải lo lắng về việc bị vượt quá giới hạn.

Điều này có thể bất khả thi với một số cơ sở dữ liệu. Với MySQL, giới hạn độ rộng tối đa của một dòng (row width) là 65.535 byte. Xin nhắc lại, đó là độ rộng của cả *dòng*, không phải độ rộng của *cột*. Nếu chúng ta khai báo dù chỉ một cột với kiểu `VARCHAR` có độ rộng tối đa là 65.535, bảng sẽ không còn chỗ trống cho bất kỳ cột nào khác nữa. Tùy thuộc vào số lượng cột `VARCHAR` trong một bảng nhất định, chúng ta sẽ cần giới hạn độ rộng của từng cột ở một mức thực tế nào đó để tất cả các cột đều có thể nằm vừa vặn. Trong những trường hợp như thế này, chúng ta có thể khai báo các cột ký tự dưới dạng `TEXT`, vì các cột `TEXT` và `BLOB` được lưu trữ trong các phân đoạn riêng biệt. Do đó, tùy thuộc vào cơ sở dữ liệu, có thể có nhiều cách để giải quyết giới hạn độ rộng cột và giảm bớt nhu cầu kiểm tra độ dài chuỗi ngay trong mô hình.

Nếu có khả năng làm tràn dung lượng một cột, thì việc kiểm tra độ dài chuỗi đơn giản trong mô hình là điều hoàn toàn có cơ sở. Sẽ bất tiện biết bao nếu phải diễn dịch thông báo lỗi sau đây thành một lỗi nghiệp vụ (domain error) có ý nghĩa?

ORA-01401: inserted value too large for column

Chúng ta thậm chí không thể xác định được cột nào đã bị tràn. Tốt nhất là nên tránh hoàn toàn vấn đề này bằng cách kiểm tra độ dài chuỗi ký tự trong các tiền điều kiện của phương thức setter. Hơn nữa, việc kiểm tra độ dài không nhất thiết chỉ nhằm phục vụ ràng buộc cột của cơ sở dữ liệu. Suy cho cùng, chính bản thân miền nghiệp vụ (domain) có thể đặt ra ràng buộc về độ dài văn bản vì những lý do rất chính đáng, chẳng hạn như các ràng buộc từ những hệ thống kế thừa (legacy system) mà chúng ta tích hợp cùng.

Chúng ta cũng có thể phải cân nhắc việc thiết lập các chốt chặn kiểm tra phạm vi cận trên - cận dưới (high-low range check), và có thể là nhiều điều kiện khác nữa. Ngay cả một bước kiểm tra định dạng đơn giản, chẳng hạn như định dạng địa chỉ email, cũng là hợp lý nếu chúng ta muốn ngăn chặn một giá trị hoàn toàn phi lý liên kết với một Entity (thực thể). Chắc chắn rằng nếu các giá trị cơ bản của một Entity đơn lẻ đều hợp lý, thì việc thực hiện xác thực thô (coarse-grained validation) trên toàn bộ đối tượng và các cấu trúc tổng hợp đối tượng (object composition) sẽ trở nên dễ dàng hơn nhiều.

## Xác thực toàn bộ đối tượng (Validating Whole Objects)

Ngay cả khi chúng ta có một Entity với các thuộc tính/đặc tính hoàn toàn hợp lệ, điều đó không nhất thiết đồng nghĩa với việc toàn bộ Entity đó đã hợp lệ. Để xác thực toàn bộ một Entity, chúng ta cần có quyền truy cập vào trạng thái của toàn bộ đối tượng — tức là tất cả các thuộc tính/đặc tính của nó. Chúng ta cũng cần một mẫu thiết kế Specification (đặc tả) [Evans & Fowler, Spec] hoặc Strategy (chiến lược) [Gamma et al.] cho việc xác thực này.

Trong ngôn ngữ mẫu (pattern language) Checks của mình, Ward Cunningham [Cunningham, Checks] đã đề cập đến một số phương pháp tiếp cận việc xác thực. Một phương pháp hữu ích cho toàn bộ đối tượng là Xác thực Trì hoãn (Deferred Validation). Ward cho biết đây là "một loại kiểm tra nên được trì hoãn cho đến thời điểm muộn nhất có thể." Nó bị trì hoãn vì đây là một loại xác thực rất chi tiết, một quy trình mà chúng ta sẽ chạy trên ít nhất một đối tượng phức tạp, hoặc thậm chí là một tổ hợp các đối tượng. Vì lý do đó, chúng ta sẽ thảo luận về Deferred Validation ở phần sau như một phương tiện để giải quyết các cấu trúc tổng hợp đối tượng lớn hơn. Trong tiểu mục này, tôi giới hạn phạm vi xác thực trong những gì Ward gọi là "các bước kiểm tra của những hoạt động đơn giản hơn."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000219_b01e809077de1fbadacdb993273e3017912d4efad6056a734696da01d292c345.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000220_5f2e2c9d51eecfcec8a10d1a19b4d268eb1e4949a2bfcfb2bea77322a23979c9.png)

Bởi vì toàn bộ trạng thái của Entity phải sẵn sàng cho quá trình xác thực, một số người có thể xem đây là thời điểm thích hợp để nhúng trực tiếp logic xử lý xác thực vào bên trong chính Entity đó. Hãy hết sức thận trọng ở điểm này. Nhiều khi, logic xác thực của một đối tượng miền thay đổi thường xuyên hơn chính bản thân đối tượng miền đó. Việc nhúng logic xác thực vào bên trong một Entity cũng gán cho nó quá nhiều trách nhiệm. Bản thân nó vốn đã gánh vác trách nhiệm xử lý hành vi nghiệp vụ của miền trong khi duy trì trạng thái của chính mình.

Một thành phần xác thực có trách nhiệm xác định xem trạng thái của Entity có hợp lệ hay không. Khi thiết kế một lớp xác thực riêng biệt bằng Java, hãy đặt nó trong cùng một Module (gói/package) với Entity. Giả sử sử dụng Java, hãy khai báo các phương thức đọc (read accessor) của thuộc tính/đặc tính với phạm vi tối thiểu là protected/package, và public cũng hoàn toàn ổn. Phạm vi private sẽ không cho phép lớp xác thực đọc được trạng thái cần thiết. Nếu lớp xác thực không được đặt trong cùng một Module với Entity, mọi phương thức truy xuất thuộc tính/đặc tính bắt buộc phải là public, điều vốn không mong muốn trong nhiều trường hợp.

Lớp xác thực có thể triển khai mẫu Specification hoặc mẫu Strategy. Nếu phát hiện thấy trạng thái không hợp lệ, nó sẽ thông báo cho client hoặc ghi lại kết quả để có thể xem xét lại sau (ví dụ: sau khi xử lý theo lô/batch processing). Điều quan trọng đối với tiến trình xác thực là phải thu thập đầy đủ một tập hợp các kết quả, thay vì ném ra một ngoại lệ ngay khi vừa phát hiện dấu hiệu bất ổn đầu tiên. Hãy xem xét validator trừu tượng có thể tái sử dụng này cùng với lớp con cụ thể của nó:

```java
public abstract class Validator {
    private ValidationNotificationHandler notificationHandler;
    ...
    public Validator(ValidationNotificationHandler aHandler) {
        super();
        this.setNotificationHandler(aHandler);
    }

    public abstract void validate();

    protected ValidationNotificationHandler notificationHandler() {
        return this.notificationHandler;
    }

    private void setNotificationHandler(
            ValidationNotificationHandler aHandler) {
        this.notificationHandler = aHandler;
    }
}

```

## KHÁM PHÁ CÁC ENTITY VÀ CÁC ĐẶC TÍNH BẢN CHẤT CỦA CHÚNG (DISCOVERING ENTITIES AND THEIR INTRINSIC CHARACTERISTICS)

```java
public class WarbleValidator extends Validator {
    private Warble warble;

    public Validator(
            Warble aWarble,
            ValidationNotificationHandler aHandler) {
        super(aHandler);
        this.setWarble(aWarble);
    }
    ...
    public void validate() {
        if (this.hasWarpedWarbleCondition(this.warble())) {
            this.notificationHandler().handleError(
                "The warble is warped.");
        }
        if (this.hasWackyWarbleState(this.warble())) {
            this.notificationHandler().handleError(
                "The warble has a wacky state.");
        }
        ...
    }
}

```

Lớp `WarbleValidator` được khởi tạo cùng với một `ValidationNotificationHandler`. Bất cứ khi nào gặp phải một điều kiện không hợp lệ, `ValidationNotificationHandler` sẽ được yêu cầu xử lý điều kiện đó. `ValidationNotificationHandler` là một bản triển khai mục đích chung với phương thức `handleError()` nhận vào một thông điệp thông báo dạng `String`. Thay vào đó, chúng ta có thể tạo các bản triển khai chuyên biệt hóa có các phương thức riêng biệt cho từng loại điều kiện không hợp lệ:

```java
class WarbleValidator extends Validator {
    ...
    public void validate() {
        if (this.hasWarpedWarbleCondition(this.warble())) {
            this.notificationHandler().handleWarpedWarble();
        }
        if (this.hasWackyWarbleState(this.warble())) {
            this.notificationHandler().handleWackyWarbleState();
        }
    }
    ...
}

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000221_8b3d290d9fc45d0a8fd7864eeabe45e0b0c34d37af36530cb2c88e2d2b449a7c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000222_09160f4047ba47845d9b9e844147bc4de020d0fe3b2f2e4cc70c73144dc4b443.png)

Cách này có ưu điểm là không làm ràng buộc (coupling) các thông điệp lỗi, hoặc các khóa thuộc tính thông điệp (message property key), hay bất kỳ điều gì mang tính đặc thù của việc thông báo, vào tiến trình xác thực. Tuyệt vời hơn nữa, hãy đặt việc xử lý thông báo vào bên trong phương thức kiểm tra:

```java
class WarbleValidator extends Validator {
    ...
    public Validator(
            Warble aWarble,
            ValidationNotificationHandler aHandler) {
        super(aHandler);
        this.setWarble(aWarble);
    }
    ...
    public void validate() {
        this.checkForWarpedWarbleCondition();
        this.checkForWackyWarbleState();
        ...
    }
    ...
    protected void checkForWarpedWarbleCondition() {
        if (this.warble()...) {
            this.warbleNotificationHandler().handleWarpedWarble();
        }
    }
    ...
    protected WarbleValidationNotificationHandler warbleNotificationHandler() {
        return (WarbleValidationNotificationHandler) this.notificationHandler();
    }
}

```

Trong ví dụ này, chúng ta sử dụng một `ValidationNotificationHandler` dành riêng cho `Warble`. Nó được truyền vào như một kiểu chuẩn nhưng được ép kiểu (cast) về kiểu cụ thể khi sử dụng nội bộ. Mô hình sẽ chịu trách nhiệm thống nhất hợp đồng (contract) giữa chính nó và các client để cung cấp đúng kiểu dữ liệu.

Làm thế nào để các client đảm bảo rằng việc xác thực Entity sẽ thực sự diễn ra? Và tiến trình xử lý xác thực bắt đầu từ đâu?

Một cách là đặt một phương thức `validate()` trên tất cả các Entity yêu cầu xác thực, và có thể thực hiện điều này thông qua một Layer Supertype (siêu kiểu theo tầng):

```java
public abstract class Entity extends IdentifiedDomainObject {

```

```java
    public Entity() {
        super();
    }

```

```java
    public void validate(ValidationNotificationHandler aHandler) {
    }
}

```

Bất kỳ lớp con Entity nào cũng có thể được gọi phương thức `validate()` một cách an toàn. Nếu Entity cụ thể hỗ trợ xác thực chuyên biệt, nó sẽ được thực thi. Nếu không được hỗ trợ, hành vi sẽ là một thao tác rỗng (no-op / no operation). Nếu chỉ có một số Entity cần xác thực, có lẽ tốt nhất là chỉ nên khai báo `validate()` trên những thực thể thực sự cần nó.

Tuy nhiên, liệu các Entity có nên thực sự tự xác thực chính mình hay không? Việc sở hữu phương thức `validate()` riêng không đồng nghĩa với việc bản thân Entity phải tự thực hiện việc xác thực. Dẫu vậy, nó cho phép Entity tự quyết định thành phần nào sẽ xác thực nó, giúp giải phóng các client khỏi mối bận tâm đó:

```java
public class Warble extends Entity {
    ...
    @Override
    public void validate(ValidationNotificationHandler aHandler) {
        (new WarbleValidator(this, aHandler)).validate();
    }
    ...
}

```

Mỗi lớp con Validator chuyên biệt hóa sẽ thực hiện bất kỳ số lượng kiểm tra xác thực tinh gọn (fine-grained validation) nào tùy theo yêu cầu. Bản thân Entity không cần biết chi tiết về cách thức nó được xác thực như thế nào, nó chỉ cần biết rằng mình có thể được xác thực. Lớp con Validator độc lập này cũng cho phép tiến trình xác thực thay đổi theo một nhịp độ khác biệt so với Entity, đồng thời tạo điều kiện thuận lợi để kiểm thử thấu đáo các kịch bản xác thực phức tạp.

## Xác thực các cấu trúc tổng hợp đối tượng (Validating Object Compositions)

Chúng ta có thể sử dụng Deferred Validation cho những trường hợp mà Ward Cunningham gọi là "các hành động phức tạp hơn đòi hỏi tất cả các bước kiểm tra của những hoạt động đơn giản hơn và còn hơn thế nữa." Ở đây, chúng ta không chỉ xác định xem một Entity đơn lẻ có hợp lệ hay không, mà còn xác định xem một cụm (cluster) hoặc một cấu trúc tổng hợp gồm nhiều Entity có đồng thời cùng hợp lệ hay không, bao gồm một hoặc nhiều thể hiện Aggregate (khối kết tập). Để làm như vậy, chúng ta có thể khởi tạo lớp con Validator cụ thể với số lượng thể hiện đối tượng thích hợp. Nhưng có lẽ tốt nhất là nên quản lý loại xác thực đó thông qua một Domain Service (dịch vụ miền). Domain Service có thể sử dụng các Repository (kho lưu trữ) để đọc các thể hiện Aggregate mà nó cần xác thực. Sau đó, nó có thể kiểm tra từng thể hiện qua các bài kiểm thử nghiêm ngặt, thực hiện riêng lẻ hoặc kết hợp cùng các thể hiện khác.

Hãy quyết định xem liệu việc xác thực có phù hợp ở mọi thời điểm hay không. Đôi khi, một Aggregate hoặc một tập hợp các Aggregate lại đang nằm ở một trạng thái trung gian, tạm thời. Có lẽ chúng ta có thể mô hình hóa một trường trạng thái (status) trên một Aggregate để biểu thị điều này, nhằm ngăn chặn việc kích hoạt xác thực vào những thời điểm không thích hợp. Khi các điều kiện đã chín muồi cho việc xác thực, mô hình có thể thông báo cho các client bằng cách phát đi một Domain Event (sự kiện miền):

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000223_0dc27fb0ec7477d03cf4337a4e986def079973bf72204ed71f080ff9a37e64fc.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000224_c8edd9e43ed4b6f60724dfe5ce9ee15ea9161eeef1207cbf682d2bf170039e9b.png)

```java
public class SomeApplicationService ... {
    ...
    public void doWarbleUseCaseTask(...) {
        Warble warble = this.warbleRepository.warbleOfId(aWarbleId);

        DomainEventPublisher
            .instance()
            .subscribe(new DomainEventSubscriber<WarbleTransitioned>() {
                public void handleEvent(DomainEvent aDomainEvent) {
                    ValidationNotificationHandler handler = ...;
                    warble.validate(handler);
                    ...
                }
                public Class<WarbleTransitioned> subscribedToEventType() {
                    return WarbleTransitioned.class;
                }
            });

        warble.performSomeMajorTransitioningBehavior();
    }
}

```

Khi được client tiếp nhận, sự kiện `WarbleTransitioned` sẽ báo hiệu rằng việc xác thực lúc này đã hoàn toàn phù hợp. Cho đến thời điểm đó, client sẽ kiềm chế, chưa thực hiện việc xác thực.

## Theo dõi thay đổi (Change Tracking)

Theo đúng định nghĩa của Entity, chúng ta không nhất thiết phải theo dõi toàn bộ các thay đổi diễn ra trên trạng thái của nó trong suốt vòng đời. Chúng ta chỉ cần hỗ trợ trạng thái liên tục thay đổi của nó mà thôi. Tuy nhiên, đôi khi các chuyên gia nghiệp vụ (domain expert) lại rất quan tâm đến những sự kiện trọng yếu xảy ra trong mô hình theo dòng thời gian. Khi rơi vào trường hợp đó, việc theo dõi các thay đổi cụ thể đối với các Entity có thể mang lại nhiều lợi ích.

Cách thiết thực nhất để đạt được khả năng theo dõi thay đổi chính xác và hữu ích là sử dụng Domain Event cùng một Event Store (kho lưu trữ sự kiện). Chúng ta tạo một kiểu Event riêng biệt cho mọi lệnh làm thay đổi trạng thái (state-altering command) quan trọng được thực thi trên từng Aggregate mà các chuyên gia nghiệp vụ quan tâm. Sự kết hợp giữa tên Event và các thuộc tính của nó giúp cho việc ghi nhận thay đổi trở nên tường minh. Các Event này được xuất bản ngay khi các phương thức xử lý lệnh hoàn tất. Một đối tượng đăng ký (subscriber) sẽ đăng ký để nhận mọi Event do mô hình sinh ra. Khi nhận được, subscriber sẽ lưu Event đó vào Event Store.

Các chuyên gia nghiệp vụ có thể không bận tâm đến từng thay đổi nhỏ nhặt trong mô hình, nhưng đội ngũ kỹ thuật có thể vẫn quan tâm. Điều này thường xuất phát từ các lý do kỹ thuật, bằng cách áp dụng một mẫu thiết kế có tên là Event Sourcing (nguồn sự kiện) (4).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000225_9b7f540b04fd2edf533187b7e9cb8462332c8ea87054dc0b8e7fe0921046c116.png)

## Tổng kết (Wrap-Up)

Chúng ta đã đi qua toàn bộ các chủ đề liên quan đến Entity. Dưới đây là phần tóm lược những gì bạn đã tìm hiểu:

* Bạn đã nắm được bốn phương pháp chính để tạo định danh duy nhất (unique identity) cho Entity.
* Bạn đã hiểu tầm quan trọng của thời điểm sinh định danh, cũng như cách sử dụng surrogate identity (định danh thay thế).
* Giờ đây bạn đã biết cách làm thế nào để đảm bảo tính ổn định của các định danh.
* Chúng ta đã thảo luận về cách khám phá các đặc tính bản chất của Entity bằng cách tìm hiểu Ubiquitous Language (ngôn ngữ chung) trong Context (ngữ cảnh). Bạn đã thấy cả thuộc tính lẫn hành vi được phát hiện như thế nào.
* Cùng với hành vi cốt lõi, bạn đã xem xét các điểm mạnh và điểm yếu của việc mô hình hóa Entity khi sử dụng nhiều vai trò (multiple roles).
* Cuối cùng, bạn đã đi sâu vào chi tiết cách khởi tạo Entity, cách xác thực chúng, và cách theo dõi các thay đổi của chúng khi cần thiết.

Tiếp theo, chúng ta sẽ cùng tìm hiểu về một khối xây dựng vô cùng quan trọng trong số các công cụ mô hình hóa chiến thuật (tactical modeling tools): Value Object (đối tượng giá trị).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000226_6fc599744fe7b80c45c6d61300c97101eed47f1ba5ad743d54fcd6378f32f56b.png)

Trang này được chủ ý để trống

## Chương 6: Value Object (Chapter 6 Value Objects)

Giá là thứ bạn phải trả. Giá trị là thứ bạn nhận được. -Warren Buffett

> 💡 **Giải thích thêm:** Câu danh ngôn nổi tiếng của nhà đầu tư huyền thoại Warren Buffett: *"Price is what you pay. Value is what you get"*. Tác giả trích dẫn câu này ở đầu chương để chơi chữ với khái niệm **Value Object**: Trong thiết kế phần mềm, lập trình viên thường tốn quá nhiều "chi phí" (công sức, độ phức tạp) cho các Entity, nhưng chính các **Value Object** (đối tượng giá trị) gọn gàng, bất biến mới là thứ mang lại "giá trị" thực sự cho sự tinh giản, tính biểu đạt và độ bền vững của mô hình.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Mặc dù thường bị lu mờ trước lối tư duy thiên về thực thể (entity-think), Value Object vẫn là một khối xây dựng mang tính sống còn của DDD (Domain-Driven Design — Thiết kế Hướng miền). Những ví dụ về các đối tượng thường được mô hình hóa dưới dạng Value bao gồm các con số như 3, 10 và 293.51; các chuỗi văn bản như 'hello, world!' và 'Domain-Driven Design'; ngày tháng; thời gian; các đối tượng chi tiết hơn như họ tên đầy đủ của một người bao gồm các thuộc tính tên, tên đệm, họ và chức danh; cùng các đối tượng khác như tiền tệ, màu sắc, số điện thoại và địa chỉ bưu điện. Ngoài ra còn có những dạng phức tạp hơn nữa. Tôi sẽ bàn luận về các Value dùng để mô hình hóa những khái niệm trong miền của bạn bằng chính Ubiquitous Language (1), nhằm hiện thực hóa các mục tiêu của Domain-Driven Design.

## Hiểu rõ những lợi thế của Value (Know the Value Advantages)

Các kiểu Value dùng để đo lường, định lượng hoặc mô tả sự vật sẽ dễ tạo, dễ kiểm thử, dễ sử dụng, dễ tối ưu hóa và bảo trì hơn.

Có thể bạn sẽ ngạc nhiên khi biết rằng chúng ta nên cố gắng mô hình hóa bằng Value Object thay vì Entity ở bất cứ nơi nào có thể. Ngay cả khi một khái niệm nghiệp vụ bắt buộc phải được mô hình hóa dưới dạng một Entity, thì thiết kế của Entity đó cũng nên thiên về việc đóng vai trò là một thùng chứa Value (Value container) hơn là một thùng chứa các Entity con (child Entity container). Lời khuyên đó không dựa trên một sở thích tùy tiện. Các kiểu Value dùng để đo lường, định lượng hoặc mô tả sự vật sẽ dễ tạo, dễ kiểm thử, dễ sử dụng, dễ tối ưu hóa và bảo trì hơn rất nhiều.

## Lộ trình của chương này (Road Map to This Chapter)

* Tìm hiểu cách nắm bắt các đặc tính của một khái niệm nghiệp vụ để mô hình hóa nó dưới dạng một Value.
* Xem cách tận dụng Value Object nhằm tối thiểu hóa sự phức tạp trong tích hợp.
* Khảo sát việc sử dụng các Kiểu Chuẩn (Standard Types) của miền nghiệp vụ được thể hiện dưới dạng các Value.
* Xem xét bài học mà SaaSOvation đã rút ra về tầm quan trọng của Value.
* Tìm hiểu cách các đội ngũ tại SaaSOvation kiểm thử, triển khai và lưu trữ bền vững (persist) các kiểu Value của họ.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000227_8e14e581e74a097a1e3188bb68d845786497a999bf601d499ca7f290c72f92bd.png)

Ban đầu, các đội ngũ tại SaaSOvation đã lạm dụng quá mức việc sử dụng Entity. Tình trạng này thực tế đã bắt đầu diễn ra từ rất lâu trước khi các khái niệm `User` và `Permission` bị đan xen chằng chéo với hoạt động cộng tác (collaboration). Ngay từ khi dự án mới khởi động, họ đã đi theo lối tư duy phổ biến cho rằng mọi thành phần trong domain model của họ đều cần phải được ánh xạ sang một bảng cơ sở dữ liệu riêng, và rằng tất cả các thuộc tính đều phải dễ dàng

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000228_6bd5cbdf9579874520827d0a7a503f698fc50e069c8af67b393b68582fa505a6.png)

được thiết lập và truy xuất thông qua các phương thức accessor công khai (public). Vì mỗi đối tượng đều sở hữu một khóa chính (primary key) trong cơ sở dữ liệu, mô hình đã bị khâu chặt lại với nhau thành một đồ thị đối tượng khổng lồ và phức tạp. Ý niệm đó chủ yếu xuất phát từ góc nhìn mô hình hóa dữ liệu mà hầu hết các nhà phát triển thường mắc phải khi bị chi phối quá mức bởi các cơ sở dữ liệu quan hệ, nơi mọi thứ đều được chuẩn hóa (normalized) và tham chiếu thông qua các khóa ngoại (foreign key). Như sau này họ đã nhận ra, việc bị cuốn theo làn sóng tư duy thiên về thực thể không chỉ không cần thiết, mà còn gây tốn kém nhiều thời gian và công sức phát triển hơn.

Khi được thiết kế đúng đắn, một thể hiện Value có thể được tạo ra, trao đi và hoàn toàn quên nó đi. Chúng ta không cần phải bận tâm liệu bên sử dụng (consumer) có vô tình chỉnh sửa sai nó theo cách nào đó hay không, hoặc thậm chí liệu họ có chỉnh sửa nó hay không. Một Value có thể tồn tại ngắn ngủi hoặc dài lâu. Nó chỉ đơn thuần là một Giá trị an toàn và vô hại, đến và đi tùy theo nhu cầu.

Điều này trút bỏ một gánh nặng rất lớn khỏi tâm trí chúng ta, tương tự như bước chuyển mình từ một ngôn ngữ lập trình không có cơ chế quản lý bộ nhớ sang một ngôn ngữ có bộ thu gom rác (garbage collection). Với sự tiện lợi tối đa mà các Value đem lại, chúng ta nên mong muốn có càng nhiều đối tượng dạng này trong hệ thống càng tốt, chừng nào điều đó còn có thể biện minh được một cách hợp lý.

Vậy làm thế nào để chúng ta xác định xem một khái niệm nghiệp vụ có nên được mô hình hóa dưới dạng một Value hay không? Chúng ta phải chú ý kỹ lưỡng đến các đặc tính của nó.

Khi bạn chỉ quan tâm đến các thuộc tính của một phần tử trong mô hình, hãy phân loại nó là một VALUE OBJECT. Hãy để nó thể hiện trọn vẹn ý nghĩa của các thuộc tính mà nó truyền tải và gán cho nó những chức năng liên quan. Hãy đối xử với VALUE OBJECT như một đối tượng bất biến (immutable). Đừng gán cho nó bất kỳ định danh nào và hãy tránh xa những sự phức tạp trong thiết kế vốn chỉ cần thiết cho việc duy trì các ENTITY. [Evans, tr. 99]

Dù việc tạo một kiểu Value có thể rất dễ dàng, đôi khi những người thiếu kinh nghiệm với DDD vẫn gặp phải sự lúng túng khi cố gắng lựa chọn giữa việc mô hình hóa một Entity hay một Value trong một trường hợp cụ thể. Sự thật là ngay cả những nhà thiết kế giàu kinh nghiệm đôi lúc cũng phải trăn trở với điều này. Cùng với việc chỉ cho bạn cách thức triển khai một Value, tôi hy vọng sẽ xua tan đi phần nào sự mơ hồ xoay quanh quá trình ra quyết định vốn đôi khi gây bối rối này.

## Các đặc tính của Value (Value Characteristics)

Nhiệm vụ ưu tiên hàng đầu là hãy đảm bảo chắc chắn rằng khi mô hình hóa một khái niệm nghiệp vụ dưới dạng một Value Object, bạn đang phản ánh đúng Ubiquitous Language. Hãy coi đây là một nguyên lý bao trùm và là một đặc tính bắt buộc phải đạt được. Tôi ngầm định nguyên lý này xuyên suốt toàn bộ chương.

Khi bạn đang cố gắng quyết định xem một khái niệm có phải là một Value hay không, bạn nên xác định xem liệu nó có sở hữu phần lớn các đặc tính sau đây hay không:

* Nó đo lường, định lượng hoặc mô tả một sự vật trong miền nghiệp vụ.
* Nó có thể được duy trì ở trạng thái bất biến (immutable).
* Nó mô hình hóa một chỉnh thể khái niệm (conceptual whole) bằng cách kết hợp các thuộc tính có liên quan thành một đơn vị toàn vẹn.
* Nó có thể thay thế hoàn toàn khi kết quả đo lường hoặc mô tả có sự thay đổi.
* Nó có thể được so sánh với các đối tượng khác thông qua phép so sánh bằng theo Giá trị (Value equality).
* Nó cung cấp cho các đối tượng cộng tác các Hành vi Không Gây Tác dụng phụ (Side-Effect-Free Behavior) [Evans].

Việc tìm hiểu chi tiết từng đặc tính này sẽ giúp ích rất nhiều. Bằng cách áp dụng phương pháp này để phân tích các phần tử thiết kế trong mô hình, bạn có thể nhận ra rằng mình nên sử dụng các Value Object thường xuyên hơn rất nhiều so với trước đây.

## Đo lường, Định lượng hoặc Mô tả (Measures, Quantifies, or Describes)

Khi bạn có một Value Object thực thụ trong mô hình của mình, dù bạn có nhận ra hay không, bản thân nó không phải là một *sự vật* trong miền nghiệp vụ. Thay vào đó, nó thực chất là một khái niệm dùng để *đo lường*, *định lượng*, hoặc *mô tả* một sự vật trong miền. Một con người có tuổi tác. Tuổi tác không thực sự là một sự vật, mà nó đo lường hoặc định lượng số năm mà con người đó (sự vật) đã sống. Một con người có tên gọi. Cái tên không phải là một sự vật, mà nó mô tả con người đó (sự vật) được gọi là gì.

Đặc tính này có mối liên hệ mật thiết với đặc tính Chỉnh thể Khái niệm (Conceptual Whole).

## Bất biến (Immutable)

Một đối tượng là một Value thì không thể thay đổi được sau khi nó đã được tạo ra. 1 Khi lập trình bằng Java hoặc C#, chẳng hạn, bạn sử dụng một trong các hàm khởi tạo (constructor) của lớp Value để tạo ra một thể hiện, truyền vào dưới dạng tham số tất cả các đối tượng mà trạng thái của nó sẽ dựa vào. Các tham số này có thể là các đối tượng sẽ trực tiếp đóng vai trò làm thuộc tính của Value, hoặc chúng có thể là các đối tượng được sử dụng để suy ra một hoặc nhiều thuộc tính mới được cấu thành trong quá trình khởi tạo. Dưới đây là một ví dụ về một kiểu Value Object giữ một tham chiếu tới một Value Object khác:

1. Đôi khi một Value Object có thể được thiết kế ở dạng có thể biến đổi (mutable), nhưng nhu cầu này thường rất hiếm gặp. Tôi không đi sâu vào các Value khả biến ở đây. Nếu bạn quan tâm đến thời điểm nên sử dụng một kiểu Value khả biến, vui lòng xem khung ghi chú ở trang 101 của cuốn sách [Evans].

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000229_90b985c96e17dc6d4ed8b7e8e2b18e0c512137c5d5cc880d9da95a6586ab9b3c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000230_c3d05f5625e41601eeff02ff5fcf1fe1c9b86eda96d3dba20818470a0219846a.png)

```java
package com.saasovation.agilepm.domain.model.product;

public final class BusinessPriority implements Serializable {
    private BusinessPriorityRatings ratings;

    public BusinessPriority(BusinessPriorityRatings aRatings) {
        super();
        this.setRatings(aRatings);
        this.initialize();
    }
    ...
}

```

Bản thân việc khởi tạo đối tượng (instantiation) đơn thuần không đảm bảo rằng một đối tượng là bất biến. Sau khi đối tượng đã được khởi tạo và gán giá trị ban đầu thông qua constructor, không một phương thức nào của nó, dù là public hay ẩn kín, được phép làm biến đổi trạng thái của nó kể từ thời điểm đó trở đi. Trong ví dụ này, chỉ các phương thức `setRatings()` và `initialize()` mới có thể làm biến đổi trạng thái vì chúng chỉ được sử dụng trong phạm vi của constructor. Phương thức `setRatings()` là private/ẩn kín và không thể bị gọi từ bên ngoài thể hiện đối tượng. 2 Xa hơn nữa, lớp `BusinessPriority` phải được triển khai sao cho không có bất kỳ phương thức nào khác ngoài các constructor, dù công khai hay ẩn kín, được phép gọi phương thức setter này. Ở phần sau, tôi sẽ thảo luận về cách kiểm thử tính bất biến của các Value Object.

Tùy thuộc vào gu thiết kế của bạn, đôi khi bạn có thể thiết kế các Value Object giữ tham chiếu tới các Entity. Tuy nhiên, bạn nên có sự thận trọng nhất định. Khi các Entity được tham chiếu thay đổi trạng thái — thông qua hành vi của chính Entity đó — thì bản thân Value cũng bị thay đổi theo, điều này vi phạm tính chất bất biến. Do đó, tốt nhất bạn nên duy trì tư duy rằng các tham chiếu Entity được giữ bởi các kiểu Value chỉ nên phục vụ cho mục đích bất biến về mặt cấu tạo (compositional immutability), tính biểu đạt và sự thuận tiện. Ngược lại, nếu các Entity được lưu giữ với mục đích tường minh là nhằm biến đổi trạng thái của chúng thông qua giao diện của Value Object, thì đó có lẽ là một lý do sai lầm để gom cụm chúng lại. Hãy cân nhắc kỹ các yếu tố đối nghịch này trong khi xem xét đặc tính Hành vi Không Gây Tác dụng phụ được thảo luận ở phần sau của chương.

2. Trong một số trường hợp, các framework như các bộ ánh xạ đối tượng - quan hệ (ORM) hoặc các thư viện tuần tự hóa (cho XML, JSON, v.v.) có thể cần sử dụng các setter để tái tạo lại trạng thái của Value từ dạng tuần tự hóa của nó.

## Thách thức các giả định của bạn (Challenge Your Assumptions)

Nếu bạn nghĩ rằng đối tượng mà bạn đang thiết kế bắt buộc phải bị biến đổi bởi hành vi của chính nó, hãy tự hỏi bản thân tại sao điều đó lại cần thiết. Liệu có thể thay thế bằng việc hoán đổi đối tượng (replacement) khi Value bắt buộc phải thay đổi hay không? Việc áp dụng cách tiếp cận này ở bất cứ nơi nào có thể chính là bạn đang thiết kế hướng tới sự tinh giản.

Đôi khi việc một đối tượng có tính bất biến là điều phi lý. Điều đó hoàn toàn bình thường, và nó là dấu hiệu cho thấy đối tượng đó nên được mô hình hóa dưới dạng một Entity. Nếu phân tích của bạn dẫn tới kết luận đó, hãy tham khảo lại chương Entities (5).

## Chỉnh thể Khái niệm (Conceptual Whole)

Một Value Object có thể sở hữu chỉ một, một vài, hoặc nhiều thuộc tính riêng lẻ, mỗi thuộc tính trong số đó đều có mối liên hệ mật thiết với những thuộc tính còn lại. Từng thuộc tính đóng góp một phần quan trọng vào một tổng thể mà tập hợp các thuộc tính đó cùng nhau mô tả. Khi bị tách rời khỏi những thuộc tính khác, từng thuộc tính đơn lẻ sẽ không thể hiện được một ý nghĩa gắn kết (cohesive meaning). Chỉ khi kết hợp lại với nhau, tất cả các thuộc tính mới tạo nên thước đo hoặc sự mô tả hoàn chỉnh như mong đợi. Điều này hoàn toàn khác biệt với việc đơn thuần nhóm một tập hợp các thuộc tính lại với nhau bên trong một đối tượng. Bản thân việc gom nhóm chẳng mang lại mấy ý nghĩa nếu chỉnh thể đó thất bại trong việc mô tả thỏa đáng một sự vật khác trong mô hình.

Như Ward Cunningham đã minh họa trong mẫu thiết kế Whole Value (Giá trị Toàn vẹn) 3 của mình [Cunningham, Whole Value aka Value Object], Giá trị `{50.000.000 đô la}` có hai thuộc tính: thuộc tính `50.000.000` và thuộc tính `đô la`. Đứng riêng rẽ, các thuộc tính này sẽ mô tả một thứ gì đó khác hoặc chẳng mang ý nghĩa gì đặc biệt. Điều này đặc biệt đúng với con số `50.000.000`, nhưng chắc chắn cũng đúng với từ `đô la`. Khi đứng cùng nhau, các thuộc tính này tạo thành một chỉnh thể khái niệm mô tả một thước đo tiền tệ. Do đó, chúng ta sẽ không mong đợi một sự vật được cho là có giá trị 50.000.000 đô la lại sở hữu hai thuộc tính tách biệt để mô tả giá trị của nó: một thuộc tính số lượng (amount) mang giá trị `50.000.000` và một thuộc tính tiền tệ (currency) mang giá trị `đô la`. Bởi vì giá trị của sự vật đó không đơn thuần chỉ là `50.000.000`, và cũng không đơn thuần chỉ là `đô la`. Dưới đây là cách mô hình hóa thiếu tường minh:

```java
// mô hình hóa sai một sự vật có giá trị
public class ThingOfWorth {
    private String name;          // thuộc tính (attribute)
    private BigDecimal amount;    // thuộc tính (attribute)
    private String currency;      // thuộc tính (attribute)
    // ...
}

```

Trong ví dụ này, mô hình và các client của nó phải tự biết khi nào và làm thế nào để sử dụng kết hợp `amount` và `currency` với nhau, bởi vì chúng không tạo thành một chỉnh thể khái niệm. Điều này đòi hỏi một cách tiếp cận tốt hơn.

3. Còn được gọi là Meaningful Whole (Chỉnh thể Có ý nghĩa).

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000231_04a99fda6f30e063a579d0decaa370e00800aea36b395050ad3077497dbf7c27.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000232_d901a99aa225e365c7e0fd8695e27dbd7feabadf3438bbfb205b93681ea4a30d.png)

Để mô tả đúng đắn giá trị của một sự vật, nó không được xem như hai thuộc tính tách rời, mà phải được đối xử như một giá trị toàn vẹn: `{50.000.000 đô la}`. Dưới đây là cách nó được mô hình hóa dưới dạng một Whole Value:

```java
public final class MonetaryValue implements Serializable {
    private BigDecimal amount;
    private String currency;

    public MonetaryValue(BigDecimal anAmount, String aCurrency) {
        this.setAmount(anAmount);
        this.setCurrency(aCurrency);
    }
    ...
}

```

Nói như vậy không có nghĩa là `MonetaryValue` đã hoàn hảo và không thể cải tiến thêm. Chắc chắn rằng, việc sử dụng thêm một kiểu Value bổ sung như `Currency` sẽ rất hữu ích ở đây. Chúng ta sẽ thay thế kiểu `String` của thuộc tính `currency` bằng kiểu `Currency` mang tính biểu đạt cao hơn nhiều. Cũng có thể có lý do chính đáng để bổ sung một Factory (nhà máy sản xuất đối tượng) và có thể là một Builder (bộ dựng) [Gamma et al.] để đảm đương việc đó. Tuy nhiên, những chủ đề đó sẽ làm phân tán sự chú ý khỏi ví dụ đơn giản này vốn được dùng để tập trung vào khái niệm Whole Value.

Bởi vì tính toàn vẹn của một khái niệm trong miền nghiệp vụ là vô cùng quan trọng, tham chiếu của đối tượng cha tới một Value Object không đơn thuần chỉ là một thuộc tính (attribute). Đúng hơn, nó là một đặc tính (property) của đối tượng/sự vật cha chứa nó trong mô hình đang nắm giữ tham chiếu tới nó. Đồng ý rằng bản thân kiểu của Value Object sở hữu một hoặc nhiều thuộc tính (hai thuộc tính trong trường hợp của `MonetaryValue`). Nhưng đối với sự vật đang nắm giữ tham chiếu tới thể hiện Value Object đó, nó lại là một property. Do đó, sự vật có giá trị 50.000.000 đô la — hãy tạm gọi là `ThingOfWorth` — sẽ có một property — có thể đặt tên là `worth` — giữ một tham chiếu tới một thể hiện của Value Object vốn có hai thuộc tính cùng nhau mô tả thước đo `{50.000.000 đô la}`. Tuy nhiên, hãy nhớ rằng tên của property — có thể là `worth` — và tên kiểu của Value — có thể là `MonetaryValue` — chỉ có thể được xác định sau khi chúng ta đã thiết lập Bounded Context (2) và Ubiquitous Language của nó. Dưới đây là bản triển khai đã được cải tiến:

```java
// mô hình hóa đúng một sự vật có giá trị
public class ThingOfWorth {
    private ThingName name;       // đặc tính (property)
    private MonetaryValue worth;  // đặc tính (property)
    // ...
}

```

Đúng như dự đoán, tôi đã thay đổi `ThingOfWorth` để nó sở hữu một property có kiểu `MonetaryValue` mang tên `worth`. Việc này chắc chắn đã dọn dẹp sạch sẽ các thuộc tính vốn trước đây rất lộn xộn. Nhưng quan trọng hơn cả, giờ đây đã có một Value thể hiện một chỉnh thể trọn vẹn.

Tôi muốn hướng sự chú ý của bạn tới thay đổi thứ hai, có lẽ là một thay đổi mà bạn không ngờ tới. Tên của `ThingOfWorth` cũng có thể quan trọng đối với việc mô tả thỏa đáng không kém gì giá trị `worth` của nó. Vì vậy, tôi cũng đã thay thế kiểu `String` của `name` bằng kiểu `ThingName`. Thoạt đầu, việc sử dụng một thuộc tính `String` cho `name` có vẻ như đã đủ thấu đáo. Nhưng trong các vòng lặp phát triển sau này, bạn nhận ra rằng việc sử dụng một `String` thuần túy sẽ gây ra nhiều rắc rối. Nó đã để cho logic nghiệp vụ trọng tâm gắn liền với cái tên của một `ThingOfWorth` bị rò rỉ ra ngoài mô hình. Nó đã rò rỉ sang các phần khác của mô hình và vào cả mã nguồn của client:

```java
// các client phải tự xử lý các vấn đề về định dạng tên
String name = thingOfWorth.name();
String capitalizedName =
    name.substring(0, 1).toUpperCase() +
    name.substring(1).toLowerCase();

```

Ở đây, client đang cố gắng một cách vụng về nhằm khắc phục các vấn đề tiềm ẩn về việc viết hoa của cái tên. Bằng cách định nghĩa kiểu `ThingName` thay thế, chúng ta có thể tập trung hóa toàn bộ các mối bận tâm liên quan đến cái tên của một `ThingOfWorth`. Dựa trên ví dụ này, `ThingName` có thể tự động định dạng hoàn chỉnh tên dạng văn bản ngay khi khởi tạo, giúp giải phóng các client khỏi gánh nặng đó. Điều này nhấn mạnh sự cần thiết của việc nhân rộng các Value trên khắp mô hình, trái ngược với việc giảm thiểu tầm quan trọng và mức độ sử dụng của chúng. Giờ đây, thay vì chứa đựng ba thuộc tính ít mang ý nghĩa, `ThingOfWorth` chứa đựng hai property Value được đặt tên và định kiểu một cách chuẩn xác.

Các constructor của một lớp Value đóng vai trò rất lớn vào tính hiệu quả của một chỉnh thể khái niệm. Cùng với tính bất biến, chúng ta yêu cầu các constructor của một lớp Value phải là phương tiện đảm bảo rằng Whole Value được tạo ra chỉ trong một thao tác duy nhất. Bạn tuyệt đối không được cho phép các thuộc tính của một thể hiện Value được gán giá trị dần dần sau khi khởi tạo, như thể đang chắp vá Whole Value từng mảnh một. Thay vào đó, trạng thái cuối cùng phải được đảm bảo khởi tạo tất cả cùng một lúc, mang tính nguyên tử (atomically). Các constructor của `BusinessPriority` và `MonetaryValue` được thể hiện trước đó đã minh chứng cho điều này.

Dưới đây là một góc nhìn khác về việc lạm dụng các kiểu dữ liệu cơ bản (ví dụ: `String`, `Integer`, hoặc `Double`). Có những ngôn ngữ lập trình (chẳng hạn như Ruby) cho phép bạn vá (patch/monkey-patch) thêm hành vi mới, chuyên biệt hóa vào một lớp một cách hiệu quả. Với những năng lực như vậy, bạn có thể cân nhắc việc sử dụng, ví dụ, một giá trị số thực dấu phẩy động `double` để biểu diễn tiền tệ. Nếu cần tính toán tỷ giá hối đoái giữa các loại tiền tệ, bạn có thể chỉ cần vá thêm hành vi `convertToCurrency(Currency aCurrency)` vào lớp `Double`. Điều này thoạt nhìn có vẻ rất sành điệu trong lập trình, nhưng liệu việc tận dụng một tính năng ngôn ngữ trong trường hợp này có thực sự là một ý tưởng hay? Thứ nhất, hành vi đặc thù về tiền tệ này rất có thể sẽ bị chìm nghỉm trong một biển các trách nhiệm dấu phẩy động đa mục đích chung. Bạn bị phạt một lỗi (Strike one). Tương tự, hoàn toàn không có sự thấu hiểu nội tại nào về tiền tệ bên trong lớp `Double`. Vì vậy, bạn sẽ phải bồi đắp thêm cho kiểu mặc định của ngôn ngữ để nó hiểu nhiều hơn về tiền tệ. Suy cho cùng, bạn vẫn phải truyền vào một `Currency` để biết loại tiền tệ cần chuyển đổi sang. Bạn bị phạt lỗi thứ hai (Strike two). Quan trọng nhất, bản thân lớp `Double` không hề nói lên được điều gì tường minh về miền nghiệp vụ của bạn. Bạn đánh mất dấu vết của các mối bận tâm nghiệp vụ vì không áp dụng Ubiquitous Language. Một cú vung gậy hụt hoàn toàn. Bạn bị xử thua (Strike three).

> 💡 **Giải thích thêm:** Tác giả sử dụng thuật ngữ ẩn dụ từ môn bóng chày: *"Strike one... Strike two... Big swing and a miss. Strike three"* (Lần đánh bóng trượt thứ nhất, thứ hai, và thứ ba — dẫn đến việc cầu thủ bị loại khỏi lượt đánh / "strike out"). Ẩn dụ này nhằm nhấn mạnh rằng việc monkey-patch (vá nóng mã nguồn) kiểu `Double` để xử lý tiền tệ mắc phải 3 sai lầm chết người liên tiếp, và đến sai lầm thứ 3 (không phản ánh Ubiquitous Language) thì thiết kế này hoàn toàn thất bại.
> Nguồn tham khảo: (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000233_ae5150a89533fb1e5d096776baedc5ab826ebb5a37ca36f398fc7c8818baf8a5.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000234_1bd6c303c6f0a30a2109e60f5d4359c36b051334057f299440fd941c358d06f1.png)

## Thách thức các giả định của bạn (Challenge Your Assumptions)

Nếu bạn đang bị cám dỗ bởi việc đặt nhiều thuộc tính lên một Entity mà kết quả là làm suy yếu mối liên kết giữa các thuộc tính đó với nhau, thì rất có khả năng các thuộc tính đó nên được gom lại thành một kiểu Value duy nhất, hoặc nhiều kiểu Value. Mỗi kiểu Value nên tạo thành một chỉnh thể khái niệm phản ánh tính gắn kết cao, được đặt tên một cách thích hợp theo Ubiquitous Language của bạn. Nếu dù chỉ một thuộc tính gắn liền với một khái niệm mang tính mô tả, rất có thể việc tập trung hóa tất cả các mối bận tâm của khái niệm này sẽ nâng cao sức mạnh cho mô hình. Nếu một hoặc nhiều thuộc tính buộc phải thay đổi theo thời gian, hãy cân nhắc việc hoán đổi toàn bộ Whole Value thay vì duy trì một Entity xuyên suốt một vòng đời dài đằng đẵng.

## Khả năng thay thế hoàn toàn (Replaceability)

Trong mô hình của bạn, một Value bất biến nên được một Entity giữ dưới dạng tham chiếu chừng nào trạng thái hằng số của nó vẫn còn mô tả đúng Whole Value ở thời điểm hiện tại. Nếu điều đó không còn đúng nữa, toàn bộ Value đó sẽ được thay thế hoàn toàn bằng một Value mới đại diện cho chỉnh thể đúng đắn hiện tại.

Khái niệm về khả năng thay thế có thể dễ dàng hiểu được trong ngữ cảnh của các con số. Giả sử bạn có khái niệm về một biến `total` là một số nguyên trong miền nghiệp vụ của mình. Nếu `total` hiện đang có giá trị là 3 nhưng bây giờ bắt buộc phải là giá trị 4, dĩ nhiên bạn không thể sửa đổi chính bản thân số nguyên 3 để nó biến thành số 4 được. Thay vào đó, bạn chỉ đơn giản là gán lại `total` thành số nguyên 4:

```java
int total = 3;

// sau đó...
total = 4;

```

Điều này quá hiển nhiên, nhưng nó giúp làm sáng tỏ một luận điểm. Trong ví dụ này, chúng ta vừa thay thế giá trị `total` 3 bằng giá trị 4. Đây không phải là một sự đơn giản hóa thái quá. Đó chính xác là những gì cơ chế thay thế thực hiện, ngay cả khi một kiểu Value Object nhất định phức tạp hơn nhiều so với một số nguyên. Hãy xem xét một kiểu Value phức tạp hơn:

```java
FullName name = new FullName("Vaughn", "Vernon");

```

```java
// sau đó...
name = new FullName("Vaughn", "L", "Vernon");

```

Cái tên ban đầu là giá trị mang tính mô tả gồm tên và họ của tôi. Sau đó, Whole Value đó được thay thế bằng Whole Value gồm tên, chữ cái đầu của tên đệm và họ của tôi. Tôi đã không sử dụng một phương thức nào trên `FullName` để thay đổi trạng thái của giá trị `name` nhằm chứa thêm chữ cái đầu của tên đệm. Làm như vậy sẽ vi phạm đặc tính bất biến của kiểu Value `FullName`. Thay vào đó, chúng ta chỉ đơn giản sử dụng cơ chế thay thế Whole Value, gán cho biến tham chiếu đối tượng `name` một thể hiện hoàn toàn mới của `FullName`. (Đúng là ví dụ này chưa phải là một cách xử lý việc thay thế giàu tính biểu đạt, và một cách tiếp cận tốt hơn đang ở ngay phía trước.)

## Thách thức các giả định của bạn (Challenge Your Assumptions)

Nếu bạn đang nghiêng về việc tạo ra một Entity chỉ vì các thuộc tính của đối tượng buộc phải thay đổi, hãy thách thức những giả định của mình xem liệu đó có thực sự là mô hình đúng đắn hay không. Liệu việc thay thế đối tượng (object replacement) có thể hoạt động hiệu quả thay thế cho cách đó được không? Nhìn vào ví dụ thay thế ở trên, bạn có thể nghĩ rằng việc tạo một thể hiện mới là thiếu thực tế và thiếu tính biểu đạt. Ngay cả khi đối tượng bạn đang xử lý có cấu trúc phức tạp và thay đổi tương đối thường xuyên, thì việc thay thế không nhất thiết phải là một giải pháp phi thực tế, hay thậm chí là một giải pháp xấu xí. Một ví dụ ở phần sau sẽ minh họa Side-Effect-Free Behavior như một cách thức đơn giản và giàu tính biểu đạt để xử lý việc thay thế Whole Value.

## So sánh bằng theo Giá trị (Value Equality)

Khi một thể hiện Value Object được so sánh với một thể hiện khác, một phép kiểm tra tính bằng nhau của đối tượng (object equality) sẽ được sử dụng. Xuyên suốt toàn bộ hệ thống có thể có rất nhiều, rất nhiều thể hiện Value bằng nhau về mặt giá trị, nhưng chúng lại không phải là cùng một đối tượng duy nhất trong bộ nhớ. Tính bằng nhau được xác định bằng cách so sánh kiểu của cả hai đối tượng và sau đó là các thuộc tính của chúng. Nếu cả kiểu lẫn các thuộc tính của chúng đều bằng nhau, thì các Value được coi là bằng nhau. Hơn nữa, nếu bất kỳ hai hoặc nhiều thể hiện Value nào bằng nhau, bạn hoàn toàn có thể gán (bằng cách thay thế) bất kỳ thể hiện nào trong số các Value bằng nhau đó cho một property cùng kiểu của một Entity, và phép gán đó sẽ không làm thay đổi giá trị của property.

Dưới đây là một ví dụ về lớp `FullName` triển khai phép kiểm tra tính bằng nhau theo Giá trị:

```java
public boolean equals(Object anObject) {
    boolean equalObjects = false;

    if (anObject != null && this.getClass() == anObject.getClass()) {
        FullName typedObject = (FullName) anObject;

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000235_6d3ccc114eb64b1d476acc9a6456245b572c0d3c5a23259ddbc9c12bfafb1e2d.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000236_1f6a9ede83f6d2d479cca3cd306d8f2b776dbcf63cec9487d2fd868e51a429d8.png)

```java
        equalObjects =
            this.firstName().equals(typedObject.firstName()) &&
            this.lastName().equals(typedObject.lastName());
    }

    return equalObjects;
}

```

Mỗi thuộc tính của hai thể hiện `FullName` được so sánh với nhau (giả sử phiên bản này chỉ có tên và họ, không có tên đệm). Nếu tất cả các thuộc tính ở cả hai đối tượng đều bằng nhau, hai thể hiện `FullName` đó được coi là bằng nhau. Bản thân Value cụ thể này ngăn chặn giá trị null đối với `firstName` và `lastName` ngay khi khởi tạo. Do đó, không cần thiết phải phòng ngừa giá trị null trong các phép so sánh `equals()` của từng property tương ứng. Ngoài ra, tôi ủng hộ việc sử dụng cơ chế tự đóng gói (self-encapsulation), nên tôi truy cập các thuộc tính thông qua các phương thức truy vấn (query method) của chúng. Điều này cho phép sử dụng các thuộc tính dẫn xuất (derived attribute) thay vì bắt buộc mỗi thuộc tính phải tồn tại dưới dạng một trạng thái tường minh. Kèm theo đó cũng ngầm định sự cần thiết của một bản triển khai `hashCode()` tương ứng (sẽ được minh họa sau).

Hãy xem xét sự kết hợp của các đặc tính Value cần thiết để hỗ trợ định danh duy nhất của Aggregate (10). Chúng ta cần khả năng so sánh bằng theo Giá trị, ví dụ như khi chúng ta truy vấn tìm một thể hiện Aggregate cụ thể theo định danh. Tính bất biến cũng tối quan trọng. Định danh duy nhất tuyệt đối không bao giờ được phép thay đổi, và điều này một phần có thể được đảm bảo thông qua đặc tính bất biến của Value. Chúng ta cũng được hưởng lợi từ đặc tính chỉnh thể khái niệm, bởi vì định danh được đặt tên theo Ubiquitous Language và chứa đựng toàn bộ các thuộc tính xác định tính độc nhất trong một thể hiện duy nhất. Tuy nhiên, trong trường hợp cụ thể này, chúng ta không cần đến đặc tính thay thế của một Value Object bởi vì định danh duy nhất của một Aggregate Root sẽ không bao giờ bị thay thế. Dẫu vậy, việc không có nhu cầu về đặc tính thay thế không hề tước đi quyền sử dụng một Value ở đây. Hơn nữa, nếu định danh đòi hỏi một số Side-Effect-Free Behavior nào đó, nó sẽ được triển khai ngay trên chính kiểu Value đó.

## Thách thức các giả định của bạn (Challenge Your Assumptions)

Hãy tự hỏi bản thân xem liệu khái niệm bạn đang thiết kế có bắt buộc phải là một Entity được định danh độc nhất tách biệt với tất cả các đối tượng khác hay không, hay nó hoàn toàn có thể được hỗ trợ thỏa đáng bằng cách sử dụng phép so sánh bằng theo Giá trị. Nếu bản thân khái niệm đó không đòi hỏi một định danh duy nhất, hãy mô hình hóa nó dưới dạng một Value Object.

## Hành vi Không Gây Tác dụng phụ (Side-Effect-Free Behavior)

Một phương thức của một đối tượng có thể được thiết kế như một Hàm Không Gây Tác dụng phụ (Side-Effect-Free Function) [Evans]. Một hàm là một thao tác của một đối tượng tạo ra kết quả đầu ra nhưng không làm thay đổi trạng thái của chính nó. Vì không có bất kỳ sự biến đổi trạng thái nào diễn ra khi thực thi một thao tác cụ thể, thao tác đó được gọi là không gây tác dụng phụ (side-effect-free). Tất cả các phương thức của một Value Object bất biến bắt buộc phải là các Side-Effect-Free Function vì chúng không được phép vi phạm tính chất bất biến của nó. Bạn có thể coi đặc tính này là một thể thống nhất không thể tách rời với tính bất biến. Chúng gắn bó vô cùng chặt chẽ. Tuy nhiên, tôi muốn tách nó ra thành một đặc tính riêng biệt vì làm như vậy sẽ làm nổi bật một lợi ích to lớn của Value Object. Nếu không, chúng ta có thể sẽ chỉ nhìn nhận Value như những thùng chứa thuộc tính thuần túy, mà bỏ qua một trong những khía cạnh mạnh mẽ nhất của mẫu thiết kế này.

## Phong cách Lập trình Hàm (The Functional Way)

Các ngôn ngữ lập trình hàm (functional programming language) nhìn chung luôn áp đặt chặt chẽ đặc tính này. Trên thực tế, các ngôn ngữ hàm thuần túy không cho phép bất cứ điều gì ngoại trừ Side-Effect-Free Behavior, đòi hỏi tất cả các closure (bao đóng) chỉ được tiếp nhận và tạo ra các Value Object bất biến.

Bertrand Meyer đã mô tả các Hàm Không Gây Tác dụng phụ chính là các phương thức Truy vấn (Query method) trong nguyên lý Phân tách Lệnh - Truy vấn (Command-Query Separation principle — CQS) của ông, như Martin Fowler đã thảo luận trong tài liệu [Fowler, CQS]. Một phương thức truy vấn là phương thức đặt một câu hỏi cho một đối tượng. Theo đúng định nghĩa, việc hỏi một đối tượng một câu hỏi tuyệt đối không được làm thay đổi câu trả lời.

Dưới đây là một ví dụ về việc kiểu `FullName` sử dụng Side-Effect-Free Behavior để tạo ra một giá trị thay thế mới cho chính nó:

```java
FullName name = new FullName("Vaughn", "Vernon");

```

```java
// sau đó...
name = name.withMiddleInitial("L");

```

Lệnh này tạo ra cùng một kết quả như ví dụ đã thảo luận trong phần "Khả năng thay thế hoàn toàn", nhưng theo một cách giàu tính biểu đạt hơn nhiều. Hàm Không Gây Tác dụng phụ này được triển khai như sau:

```java
public FullName withMiddleInitial(String aMiddleNameOrInitial) {
    if (aMiddleNameOrInitial == null) {
        throw new IllegalArgumentException(
            "Must provide a middle name or initial.");
    }

    String middle = aMiddleNameOrInitial.trim();

    if (middle.isEmpty()) {
        throw new IllegalArgumentException(
            "Must provide a middle name or initial.");
    }

    return new FullName(
        this.firstName(),
        middle.substring(0, 1).toUpperCase(),
        this.lastName());
}

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000237_fa2ffaaf1d0ae4e561537c8a5ac8b1c566b8d506ab356c78393980bcbc051160.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000238_f54a2018a99c1b85611719095d4dbc8da4eda0f7ac4eabde34dc6a799bc426df.png)

Trong ví dụ này, phương thức `withMiddleInitial()` không hề làm biến đổi trạng thái của chính bản thân thể hiện Value của nó, và do đó, nó hoàn toàn không gây tác dụng phụ. Thay vào đó, nó khởi tạo một thể hiện Value mới được cấu thành từ một số thành phần sẵn có của chính nó kết hợp với chữ cái đầu của tên đệm được cung cấp. Phương thức này đã đóng gói logic nghiệp vụ quan trọng của miền vào ngay bên trong mô hình thay vì để nó bị rò rỉ ra ngoài mã nguồn của client, điều vốn rất dễ xảy ra như trong ví dụ trước đó.

## Khi một Value tham chiếu tới một Entity (When a Value References an Entity)

Liệu một phương thức của Value Object có nên được phép làm biến đổi một Entity được truyền vào dưới dạng tham số hay không? Chưa bàn đến việc đặt ra một quy tắc, nếu một phương thức như vậy thực sự gây ra sự biến đổi cho một Entity, liệu nó có thực sự là không gây tác dụng phụ hay không? Liệu việc kiểm thử phương thức đó có dễ dàng hay không? Tôi khẳng định là không dễ, hoặc ít nhất là kém dễ dàng hơn nhiều. Do đó, khi một phương thức của Value nhận một Entity làm tham số, tốt nhất là nó chỉ nên trả về một kết quả để Entity đó có thể tự sử dụng nhằm biến đổi chính mình theo các quy tắc riêng của nó.

Dẫu vậy, vẫn có những vấn đề tồn tại với một thiết kế như vậy. Hãy xem xét một ví dụ. Ở đây một `Product` trong Scrum, vốn là một Entity, được sử dụng theo cách nào đó bởi `BusinessPriority`, một Value Object, để tính toán mức độ ưu tiên:

```java
float priority = businessPriority.priorityOf(product);

```

Bạn có nhìn thấy những khiếm khuyết trong cách làm này không? Chắc hẳn bạn đã nhận ra ít nhất một vài vấn đề:

* Điều tôi muốn hướng sự chú ý tới là chúng ta đang ép buộc Value không chỉ phụ thuộc vào một `Product`, mà còn phải hiểu rõ cấu trúc hình dạng của Entity này. Ở bất cứ nơi nào có thể, hãy giới hạn một Value chỉ phụ thuộc vào và hiểu về chính kiểu của nó cùng kiểu của các thuộc tính bên trong nó. Điều đó không phải lúc nào cũng khả thi, nhưng luôn là một mục tiêu rất tốt đẹp.
* Một người nào đó khi đọc mã nguồn sẽ không thể biết được những phần nào của `Product` sẽ thực sự được sử dụng. Biểu thức này không mang tính tường minh, điều làm suy yếu độ rõ ràng của mô hình. Sẽ tốt hơn rất nhiều nếu một property thực tế hoặc property dẫn xuất nào đó của `Product` được truyền vào.
* Quan trọng hơn đối với cuộc thảo luận này, bất kỳ phương thức nào của Value nhận một Entity làm tham số đều không thể dễ dàng chứng minh được rằng nó không gây ra sự biến đổi cho Entity đó, khiến thao tác này trở nên khó kiểm thử hơn. Vì vậy, ngay cả khi một Value hứa hẹn sẽ không gây ra sự thay đổi, thì cũng không ai có thể dễ dàng chứng minh được rằng nó thực sự không làm điều đó.

Dựa trên phân tích này, chúng ta thực sự chưa cải thiện được điều gì ở đây cả. Để thay đổi điều đó và làm cho Value trở nên vững chắc, bạn chỉ nên truyền các Value làm tham số cho các phương thức của Value. Bằng cách này, bạn sẽ đạt được mức độ cao nhất của Side-Effect-Free Behavior. Việc này không hề khó thực hiện:

```java
float priority =
    businessPriority.priority(product.businessPriorityTotals());

```

Ở đây, chúng ta chỉ đơn giản yêu cầu `Product` cung cấp một thể hiện của Value `BusinessPriorityTotals`. Bạn có thể cho rằng `priority()` nên trả về một kiểu dữ liệu khác thay vì kiểu `float`. Điều đó sẽ đặc biệt đúng nếu việc thể hiện một mức độ ưu tiên cần phải là một phần chính thức hơn trong Ubiquitous Language, trong trường hợp đó một kiểu giá trị tùy biến sẽ là lựa chọn phù hợp. Những quyết định như thế này xuất hiện như một kết quả của quá trình liên tục tinh chỉnh mô hình. Thật vậy, sau khi phân tích, đội ngũ SaaSOvation nhận thấy rằng Entity `Product` không nên tự mình tính toán tổng mức độ ưu tiên kinh doanh. Công việc đó cuối cùng sẽ được thực hiện bởi một Domain Service (7), và bạn sẽ thấy giải pháp tốt hơn trong chương đó.

Nếu bạn quyết định không thiết kế một Value Object chuyên biệt hóa mà chọn sử dụng một kiểu Value cơ bản của ngôn ngữ thay thế (kiểu nguyên thủy primitive hoặc kiểu bao bọc wrapper), bạn có thể đang làm suy giảm giá trị mô hình của mình. Bạn sẽ không có cơ hội gán các Side-Effect-Free Function đặc thù của miền nghiệp vụ cho kiểu Value cơ bản của ngôn ngữ đó. Mọi hành vi chuyên biệt sẽ bị tách rời khỏi Value. Và ngay cả khi ngôn ngữ lập trình của bạn cho phép bạn vá (patch) thêm hành vi mới vào kiểu cơ bản, liệu điều đó có thực sự giúp bạn nắm bắt được những hiểu biết sâu sắc về miền nghiệp vụ hay không?

## Thách thức các giả định của bạn (Challenge Your Assumptions)

Nếu bạn nghĩ rằng một phương thức cụ thể không thể không gây tác dụng phụ và buộc phải làm biến đổi trạng thái của chính thể hiện của nó, hãy thách thức những giả định của bạn. Liệu có cách nào để áp dụng cơ chế thay thế thay vì biến đổi trạng thái hay không? Ví dụ trước đó cung cấp một cách tiếp cận rất đơn giản để tạo ra một Value mới bằng cách tái sử dụng các phần của Value hiện có và chỉ thay thế những phần thực sự bị thay đổi. Rất hiếm khi mọi đối tượng trong hệ thống đều là một Value. Một số đối tượng gần như chắc chắn sẽ là Entity. Hãy so sánh cẩn trọng các tiêu chuẩn đặc tính của Value với các tiêu chuẩn của Entity. Một lượng thời gian suy nghĩ và thảo luận hợp lý trong nhóm sẽ dẫn tới những kết luận chính xác.

Một khi các đội ngũ tại SaaSOvation đọc được những chỉ dẫn của [Evans] về các Hàm Không Gây Tác dụng phụ, cùng các tài liệu khác về Whole Value, họ đã nhận ra rằng mình nên sử dụng các Value Object thường xuyên hơn rất nhiều. Các đội ngũ kể từ đó đã nhận thức được rằng việc thấu hiểu các đặc tính của Value nêu trên đã thực sự giúp họ khám phá ra nhiều kiểu Value tự nhiên hơn trong miền nghiệp vụ của mình.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000239_3a8a0b8e557326f6c989bd4872bc989a1c75de11feeff96c5f24a006c2bf7cd6.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000240_9fd2a4909f97db32464d607e69828ec0288bbc14f41a744be39940c169081f09.png)

## Có phải mọi thứ đều là Value Object? (Is Everything a Value Object?)

Đến lúc này, có thể bạn đã bắt đầu nghĩ rằng mọi thứ trông đều giống như một Value Object. Suy nghĩ đó vẫn tốt hơn là việc nghĩ rằng mọi thứ trông đều giống như một Entity. Nơi bạn có thể cần một chút thận trọng là khi gặp phải những thuộc tính thực sự đơn giản mà hoàn toàn không cần bất kỳ sự xử lý đặc biệt nào. Có lẽ đó là các biến kiểu Boolean hoặc bất kỳ giá trị số nào thực sự độc lập, không cần thêm sự hỗ trợ chức năng nào, và không liên quan đến bất kỳ thuộc tính nào khác trong cùng một Entity. Đứng một mình, các thuộc tính đơn giản đó đã là một Meaningful Whole. Dẫu vậy, bạn hoàn toàn có thể phạm phải "sai lầm" khi bao bọc không cần thiết một thuộc tính đơn lẻ vào trong một kiểu Value mà không có chức năng đặc biệt nào, và bạn vẫn ở vị thế tốt hơn nhiều so với những người không bao giờ thèm đoái hoài đến việc thiết kế Value. Nếu nhận thấy mình đã làm hơi quá tay một chút, bạn luôn có thể tái cấu trúc lại đôi chút.

## Tích hợp theo phong cách tối giản (Integrate with Minimalism)

Luôn có nhiều Bounded Context trong mỗi sáng kiến áp dụng DDD, điều đó đồng nghĩa với việc chúng ta phải tìm ra những phương thức thích hợp để tích hợp chúng. Bất cứ nơi nào có thể, hãy sử dụng các Value Object để mô hình hóa các khái niệm trong Context xuôi dòng (downstream Context) khi các đối tượng từ Context ngược dòng (upstream Context) truyền vào. Bằng cách làm như vậy, bạn có thể tích hợp với ưu tiên đặt vào tính tối giản, tức là tối thiểu hóa số lượng thuộc tính mà bạn phải chịu trách nhiệm quản lý trong mô hình xuôi dòng của mình. Việc sử dụng các Value bất biến đồng nghĩa với việc bạn gánh vác ít trách nhiệm hơn.

## Tại sao lại phải gánh vác quá nhiều trách nhiệm? (Why Be So Responsible?)

Việc sử dụng các Value bất biến đồng nghĩa với việc bạn gánh vác ít trách nhiệm hơn.

Sử dụng lại một ví dụ từ chương Bounded Contexts (2), hãy nhớ lại rằng hai Aggregate trong *Identity and Access Context* ở thượng nguồn có tác động tới *Collaboration Context* ở hạ nguồn, như được minh họa trong Hình 6.1. Trong Identity and Access Context, hai Aggregate đó là `User` và `Role`. Collaboration Context quan tâm đến việc liệu một `User` cụ thể có đóng một `Role` cụ thể hay không, cụ thể là Moderator (Điều hành viên). Collaboration Context sử dụng Anticorruption Layer (Lớp Chống Tha hóa) (3) của mình để truy vấn Open Host Service (Dịch vụ Máy chủ Mở) (3) của Identity and Access Context. Nếu truy vấn tích hợp cho thấy vai trò Moderator đang được đảm nhiệm bởi người dùng cụ thể đó, Collaboration Context sẽ tạo ra một đối tượng đại diện, cụ thể là một `Moderator`.

Hình 6.1 Đối tượng Moderator trong Context của nó dựa trên trạng thái của một User và Role trong một Context khác. User và Role là các Aggregate, nhưng Moderator lại là một Value Object.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000241_d04333eb041a7f254606b5537a7bc24752c7c3c121b68aeebeda48e912bc80a9.png)