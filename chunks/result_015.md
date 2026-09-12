Một lựa chọn có sẵn với cơ chế ánh xạ đối tượng - quan hệ (object-relational mapping) của Hibernate (framework ORM phổ biến trong Java) là serialize (tuần tự hóa đối tượng thành chuỗi ký tự) toàn bộ collection (tập hợp) các đối tượng thành một biểu diễn dạng văn bản rồi persist (lưu trữ bền vững vào cơ sở dữ liệu) biểu diễn đó vào một cột đơn lẻ. Cách tiếp cận này tồn tại một số nhược điểm. Tuy nhiên, trong một số trường hợp, các nhược điểm này không quá phiền toái và có thể bỏ qua ngay để tận dụng những ưu điểm mà lựa chọn này mang lại. Trong các tình huống đó, bạn có thể quyết định áp dụng tùy chọn lưu trữ Value collection (tập hợp các Value Object - đối tượng giá trị) này. Dưới đây là các nhược điểm tiềm ẩn cần cân nhắc:

- **Độ rộng cột (Column width).** Đôi khi bạn không thể xác định trước số lượng phần tử Value tối đa trong collection, hoặc kích thước tối đa của mỗi Value sau khi đã serialize. Ví dụ, một số collection đối tượng có thể chứa số lượng phần tử tùy ý mà không có giới hạn trên xác định. Ngoài ra, mỗi phần tử Value trong collection có thể có độ dài ký tự chuỗi biểu diễn sau khi serialize không cố định. Điều này thường xảy ra khi một hoặc nhiều thuộc tính của kiểu Value có kiểu String với độ dài ký tự lớn hoặc không giới hạn. Trong một hoặc cả hai tình huống kể trên, hoàn toàn có khả năng dạng thức tuần tự hóa của từng phần tử hoặc của toàn bộ collection sẽ vượt quá độ rộng tối đa cho phép của một cột kiểu ký tự. Vấn đề này có thể còn trầm trọng hơn nếu các cột ký tự có độ rộng tối đa tương đối hẹp, hoặc do tổng dung lượng byte tối đa cho phép để lưu trữ một hàng dữ liệu bị giới hạn. Chẳng hạn, dù storage engine (công cụ lưu trữ) InnoDB của MySQL cho phép độ rộng tối đa của VARCHAR lên tới 65.535 ký tự, nó cũng đồng thời áp đặt giới hạn tổng cộng 65.535 byte lưu trữ cho một hàng đơn lẻ. Bạn phải chừa đủ dung lượng cho các cột khác để lưu trữ toàn bộ một Entity (thực thể, có định danh duy nhất). Hệ quản trị cơ sở dữ liệu Oracle Database lại giới hạn độ rộng tối đa của VARCHAR2 / NVARCHAR2 ở mức 4.000 ký tự. Nếu không thể xác định trước độ rộng tối đa cần thiết để lưu trữ biểu diễn tuần tự hóa của một Value collection và/hoặc độ rộng tối đa của cột có nguy cơ bị tràn, bạn nên tránh dùng lựa chọn này.
- **Bắt buộc phải truy vấn (Must query).** Vì theo phong cách này, các Value collection được tuần tự hóa thành một chuỗi văn bản phẳng, các thuộc tính của từng phần tử Value riêng lẻ sẽ không thể đưa vào biểu thức truy vấn SQL. Nếu bất kỳ thuộc tính nào của Value bắt buộc phải hỗ trợ truy vấn, bạn không thể sử dụng phương án này. Tuy nhiên, đây có thể là lý do ít gặp hơn để phải né tránh giải pháp này, bởi vì nhu cầu truy vấn một hoặc nhiều thuộc tính từ các đối tượng nằm bên trong một collection nội bộ vốn khá hiếm hoi.
- **Yêu cầu kiểu người dùng tùy biến (Requires custom user type).** Để áp dụng cách tiếp cận này, bạn phải tự phát triển một Hibernate custom user type (kiểu người dùng tùy biến trong Hibernate) nhằm quản lý việc serialization (tuần tự hóa) và deserialization (giải tuần tự hóa từ chuỗi về đối tượng) cho từng collection. Về mặt cá nhân, tôi thấy điều này ít gây phiền toái hơn các mối bận tâm kể trên, bởi vì chỉ cần một triển khai custom user type duy nhất được thiết kế chỉn chu là đã có thể hỗ trợ collection của mọi kiểu Value Object (theo tiêu chí "một giải pháp dùng chung cho tất cả" - one size fits all).

Tôi không cung cấp sẵn mã nguồn của một Hibernate custom user type để quản lý việc tuần tự hóa collection vào một cột duy nhất ở đây, nhưng cộng đồng Hibernate đã chia sẻ rất nhiều tài liệu hướng dẫn giúp bạn tự triển khai phiên bản của riêng mình.

## ORM và nhiều Value được lưu dưới dạng một Entity trong cơ sở dữ liệu

Một cách tiếp cận rất trực diện để lưu trữ bền vững một collection các thể hiện Value bằng Hibernate (hoặc các ORM khác) cùng một cơ sở dữ liệu quan hệ là xem kiểu Value như một entity trong data model (mô hình dữ liệu). Để nhắc lại điều tôi từng khẳng định trong phần "Từ chối ảnh hưởng không đáng có của việc rò rỉ mô hình dữ liệu" (Reject Undue Influence of Data Model Leakage), cách tiếp cận này tuyệt đối không được dẫn đến việc mô hình hóa sai lệch một khái niệm thành Entity trong domain model (mô hình miền nghiệp vụ) chỉ vì nó được biểu diễn tốt nhất dưới dạng một database entity nhằm phục vụ mục đích lưu trữ. Chính sự object-relational impedance mismatch (sự lệch pha kiến trúc giữa lập trình hướng đối tượng và cơ sở dữ liệu quan hệ) trong một số trường hợp đã đòi hỏi cách tiếp cận này, chứ không phải do một nguyên lý DDD (Domain-Driven Design - Thiết kế hướng miền) nào quy định. Nếu có sẵn một phong cách lưu trữ hoàn toàn tương thích, bạn chắc chắn sẽ mô hình hóa khái niệm đó như một kiểu Value mà không cần phải đắn đo suy nghĩ về các đặc tính của một database entity. Tư duy theo cách này sẽ giúp định hình tư duy mô hình hóa miền của chúng ta một cách đúng đắn.

Để đạt được mục tiêu này, chúng ta có thể áp dụng mẫu thiết kế Layer Supertype (tầng siêu kiểu - lớp cha dùng chung cho các lớp trong cùng một tầng kiến trúc) [Fowler, P of EAA]. Về mặt cá nhân, tôi cảm thấy an tâm hơn khi giấu kín surrogate identity (khóa thay thế / khóa giả lập sinh tự động, hay primary key) cần thiết này đi. Tuy nhiên, vì mọi Object trong Java (cũng như các ngôn ngữ khác) đều đã sở hữu một định danh duy nhất nội bộ chỉ do máy ảo sử dụng, bạn hoàn toàn có thể cảm thấy việc gắn thêm một định danh chuyên biệt trực tiếp vào Value là hợp lý. Tôi cho rằng dù nghiêng về cách tiếp cận nào, khi xử lý bài toán lệch pha giữa đối tượng và quan hệ, chúng ta đều cần xây dựng một lý do thuyết phục trong tư duy kỹ thuật để giải thích cho lựa chọn của mình. Sở thích của tôi sẽ được trình bày ngay sau đây.

Dưới đây là một ví dụ về cách tiếp cận surrogate key mà tôi ưa thích, sử dụng hai lớp Layer Supertype:

```java
public abstract class IdentifiedDomainObject

```

```java
implements Serializable {
    private long id = -1;

    public IdentifiedDomainObject() {
        super();
    }

    protected long id() {
        return this.id;
    }

    protected void setId(long anId) {
        this.id = anId;
    }
}

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000267_6d6eeae6de5481291d053c857f7c99c0958a08a70d87d3fe2701d53f843af578.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000268_1aa54b23830a23bd1b66328a26d6d19da38df3cdc7bed0226e7a61a813dff02e.png)

Lớp Layer Supertype đầu tiên tham gia vào đây là `IdentifiedDomainObject`. Lớp cơ sở trừu tượng này cung cấp một surrogate primary key cơ bản được ẩn hoàn toàn khỏi tầm nhìn của các lớp client. Vì các accessor method (phương thức truy cập getter/setter) được khai báo với phạm vi `protected`, client sẽ không bao giờ phải băn khoăn liệu các phương thức đó có dành cho mình sử dụng hay không. Tất nhiên, bạn còn có thể triệt tiêu hoàn toàn sự hiện diện của các phương thức này bằng cách khai báo phạm vi `private`. Hibernate hoàn toàn có khả năng sử dụng cơ chế reflection (phản chiếu) trên phương thức hoặc trường dữ liệu ở bất kỳ phạm vi truy cập nào ngoài `public`.

Tiếp theo, tôi cung cấp thêm một Layer Supertype chuyên biệt dành riêng cho các Value Object:

```java
public abstract class IdentifiedValueObject

```

```java
extends IdentifiedDomainObject {
    public IdentifiedValueObject() {
        super();
    }
}

```

Bạn có thể xem lớp `IdentifiedValueObject` đơn thuần là một marker class (lớp đánh dấu), một lớp con không chứa hành vi kế thừa từ `IdentifiedDomainObject`. Riêng tôi coi nó có giá trị như một tài liệu trong mã nguồn, vì nó giúp làm rõ ràng hơn thách thức mô hình hóa mà nó đang giải quyết. Cùng với hướng đi đó, lớp `IdentifiedDomainObject` có một lớp con trừu tượng trực tiếp thứ hai tên là `Entity`, vốn được thảo luận trong Chương 5 (Entities). Tôi thích cách tiếp cận này. Bạn cũng có thể chọn cách lược bỏ các lớp bổ sung này nếu muốn.

Giờ đây, khi đã có một phương tiện thuận tiện và được che giấu kỹ càng để gắn surrogate identity cho bất kỳ kiểu Value nào, sau đây là lớp mẫu đưa nó vào sử dụng:

```java
public final class GroupMember extends IdentifiedValueObject {
    private String name;
    private TenantId tenantId;
    private GroupMemberType type;

    public GroupMember(
            TenantId aTenantId,
            String aName,
            GroupMemberType aType) {
        this();
        this.setName(aName);
        this.setTenantId(aTenantId);
        this.setType(aType);
        this.initialize();
    }
    ...
}

```

Lớp `GroupMember` là một kiểu Value được tập hợp bởi Root Entity (thực thể gốc) của lớp Aggregate (cụm thực thể / cốt lõi phân định nghiệp vụ) `Group`. Root Entity này chứa một số lượng tùy ý các thể hiện `GroupMember`. Giờ đây, khi mỗi thể hiện `GroupMember` đã được định danh duy nhất trong data model thông qua surrogate primary key của nó, chúng ta hoàn toàn tự do ánh xạ việc lưu trữ nó như một database entity trong khi vẫn giữ nguyên bản chất là một Value trong domain model. Đây là phần mã nguồn liên quan của lớp `Group`:

```java
public class Group extends Entity {
    private String description;
    private Set<GroupMember> groupMembers;
    private String name;
    private TenantId tenantId;

    public Group(
            TenantId aTenantId,
            String aName,
            String aDescription) {
        this();
        this.setDescription(aDescription);
        this.setName(aName);
        this.setTenantId(aTenantId);
        this.initialize();
    }
    ...
    protected Group() {
        super();
        this.setGroupMembers(new HashSet<GroupMember>(0));
    }
    ...
}

```

Lớp `Group` sẽ dần dần tích lũy một số lượng tùy ý các thể hiện `GroupMember` trong tập hợp `Set` mang tên `groupMembers` của nó. Hãy ghi nhớ rằng nếu bạn có ý định thay thế toàn bộ collection, hãy luôn sử dụng phương thức `clear()` của `Collection` trước khi gán mới. Làm như vậy đảm bảo rằng triển khai `Collection` ngầm định của Hibernate sẽ xóa các phần tử lỗi thời khỏi kho dữ liệu. Đoạn mã dưới đây không phải là một phương thức thực tế của lớp `Group`, mà chỉ là ví dụ minh họa cách thức tổng quát để tránh tình trạng các phần tử Value bị mồ côi (orphaned) khi thực hiện thay thế toàn bộ collection:

```java
public void replaceMembers(Set<GroupMember> aReplacementMembers) {

```

```java
    this.groupMembers().clear();
    this.setGroupMembers(aReplacementMembers);
}

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000269_9b7201e3672ca386355f3cd3f218a1900ce21a01bb0edab5668cc9ef9520f7b0.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000270_bb74dfc8e1ce06fe843555afd8c22be24fabab713d055e431bcc564685282ec1.png)

Tôi cho rằng sự rò rỉ cơ chế ORM vào domain model như thế này không gây phiền toái vì nó tận dụng tiện ích `Collection` chuẩn mực phổ biến, và hơn nữa phía client hoàn toàn không nhìn thấy nó. Việc đồng bộ nội dung collection với cơ sở dữ liệu không phải lúc nào cũng đòi hỏi sự tính toán phức tạp. Hành động xóa một phần tử Value đơn lẻ trong kho dữ liệu đã được tự động xử lý khi sử dụng phương thức `remove()` của `Collection`, do đó trong tình huống này hoàn toàn không có sự rò rỉ ORM nào xảy ra.

Tiếp theo, chúng ta quan tâm đến đoạn cấu hình ánh xạ của `Group` dùng để ánh xạ collection:

```xml
<hibernate-mapping>
    <class name="com.saasovation.identityaccess.domain.model.identity.Group" table="tbl_group" lazy="true">
        ...
        <set name="groupMembers" cascade="all,delete-orphan" inverse="false" lazy="true">
            <key column="group_id" not-null="true" />
            <one-to-many class="com.saasovation.identityaccess.domain.model.identity.GroupMember" />
        </set>
        ...
    </class>
</hibernate-mapping>

```

Tập hợp `Set` của `groupMembers` được ánh xạ hoàn toàn tương tự như một database entity. Ngoài ra, chúng ta cùng xem cấu hình ánh xạ đầy đủ của `GroupMember`:

```xml
<hibernate-mapping>
    <class name="com.saasovation.identityaccess.domain.model.identity.GroupMember" table="tbl_group_member" lazy="true">
        <id name="id" type="long" column="id" unsaved-value="-1">
            <generator class="native"/>
        </id>
        <property name="name" column="name" type="java.lang.String" update="true" insert="true" lazy="false" />

```

```xml
        <component name="tenantId" class="com.saasovation.identityaccess.domain.model.identity.TenantId">
            <property name="id" column="tenant_id_id" type="java.lang.String" update="true" insert="true" lazy="false" />
        </component>
        <property name="type" column="type" type="com.saasovation.identityaccess.infrastructure.persistence.GroupMemberTypeUserType" update="true" insert="true" not-null="true" />
    </class>
</hibernate-mapping>

```

Hãy chú ý đến thẻ `<id>` định nghĩa surrogate primary key phục vụ việc lưu trữ. Và cuối cùng, dưới đây là định nghĩa bảng `tbl_group_member` tương ứng trong MySQL:

```sql
CREATE TABLE `tbl_group_member` (
    `id` int(11) NOT NULL auto_increment,
    `name` varchar(100) NOT NULL,
    `tenant_id_id` varchar(36) NOT NULL,
    `type` varchar(5) NOT NULL,
    `group_id` int(11) NOT NULL,
    KEY `k_group_id` (`group_id`),
    KEY `k_tenant_id_id` (`tenant_id_id`),
    CONSTRAINT `fk_1_tbl_group_member_tbl_group` FOREIGN KEY (`group_id`) REFERENCES `tbl_group` (`id`),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;

```

Khi nhìn vào cấu hình ánh xạ và định nghĩa bảng cơ sở dữ liệu của `GroupMember`, chúng ta có cảm giác rất rõ ràng rằng mình đang làm việc với một entity. Có một khóa chính tên là `id`. Có một bảng riêng biệt cần được join (liên kết) với bảng `tbl_group`. Có một khóa ngoại (foreign key) trỏ ngược lại `tbl_group`. Dù gọi bằng bất kỳ tên nào khác thì đây thực chất vẫn là một entity, nhưng *chỉ xét thuần túy dưới góc độ của data model*. Trong domain model, `GroupMember` rõ ràng là một Value Object. Các biện pháp thích hợp đã được triển khai trong domain model nhằm che giấu cẩn thận mọi mối bận tâm về lưu trữ bền vững. Tôi không để lộ bất kỳ dấu hiệu nào cho các client của domain model biết rằng đã có sự rò rỉ tầng lưu trữ xảy ra. Thậm chí hơn thế nữa, ngay cả các lập trình viên làm việc trực tiếp trên domain model cũng phải quan sát rất kỹ mới nhận ra dấu vết của sự rò rỉ này.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000271_c798088ac4adf6860b52991b93ea8b44a3597d9decbe000b010f4268502f69bd.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000272_bb48c2928a15b64d15839f1e2272d7fe4c4b06afd6c0ad73e09ca8a4de3930a9.png)

## ORM và nhiều Value được lưu thông qua một Join Table

Hibernate cung cấp một phương thức để lưu trữ các collection đa giá trị vào một join table (bảng liên kết trung gian) mà không đòi hỏi bản thân kiểu Value phải mang bất kỳ đặc tính entity nào của data model. Kiểu ánh xạ này đơn thuần lưu các phần tử Value trong collection vào một bảng chuyên dụng, với định danh cơ sở dữ liệu của đối tượng miền Entity cha đóng vai trò là khóa ngoại. Nhờ đó, mọi phần tử Value trong collection đều có thể được truy vấn thông qua khóa ngoại định danh của cha và được tái tạo trở lại thành Value collection của mô hình. Ưu điểm nổi bật của cách tiếp cận ánh xạ này là kiểu Value không cần phải chứa một surrogate identity ẩn để thực hiện phép join. Để sử dụng tùy chọn ánh xạ Value collection này, bạn dùng thẻ `<composite-element>` của Hibernate.

Điều này thoạt nhìn có vẻ là một bước tiến lớn, và có thể nó rất phù hợp với nhu cầu của bạn. Tuy nhiên, cách tiếp cận này cũng có những điểm yếu mà bạn cần phải lưu tâm. Một nhược điểm là phép join vẫn bắt buộc phải diễn ra ngay cả khi kiểu Value của bạn không đòi hỏi surrogate key, bởi vì giải pháp này liên quan đến việc chuẩn hóa (normalization) dữ liệu trên hai bảng. Đúng là cách tiếp cận "ORM và nhiều Value được lưu dưới dạng một Entity cơ sở dữ liệu" cũng đòi hỏi phép join. Nhưng cách tiếp cận đó không bị giới hạn bởi điểm yếu thứ hai của giải pháp này, đó là . . .

Nếu collection của bạn là một `Set`, không một thuộc tính nào của kiểu Value được phép mang giá trị `null`. Nguyên nhân là vì để xóa (cơ chế dọn rác trong data model) một phần tử `Set` cụ thể, toàn bộ các thuộc tính tạo nên tính duy nhất của phần tử Value đó phải được dùng như một dạng khóa phức hợp (composite key) nhằm tìm kiếm và xóa dòng dữ liệu. Một giá trị `null` không thể tham gia vào thành phần của khóa phức hợp bắt buộc này. Dĩ nhiên, nếu bạn biết chắc rằng một kiểu Value cụ thể sẽ không bao giờ có thuộc tính mang giá trị `null`, thì đây là một cách tiếp cận khả thi — miễn là bạn không gặp thêm các yêu cầu xung đột nào khác.

Nhược điểm thứ ba của cách tiếp cận ánh xạ này là bản thân kiểu Value đang được ánh xạ không được phép chứa một collection khác bên trong nó. Hoàn toàn không có cơ chế nào để ánh xạ bằng thẻ `<composite-element>` nếu chính các phần tử đó lại chứa các collection con. Nếu kiểu Value của bạn không chứa bất kỳ loại collection nào và đáp ứng đầy đủ các điều kiện tiên quyết của phong cách ánh xạ này, bạn hoàn toàn có thể sử dụng nó.

Sau cùng, tôi nhận thấy cách tiếp cận ánh xạ này có quá nhiều hạn chế đến mức nhìn chung nên tránh sử dụng. Đối với tôi, việc gán một surrogate identity được che giấu kỹ lưỡng lên kiểu Value nằm trong mối quan hệ một-nhiều (one-to-many) đơn giản hơn nhiều, và không phải lo lắng về bất kỳ ràng buộc nào của `<composite-element>`. Bạn có thể có quan điểm khác, và giải pháp này chắc chắn vẫn phát huy tác dụng tốt nếu mọi yếu tố mô hình hóa của bạn đều rơi vào điều kiện thuận lợi.

## ORM và các đối tượng Enum đóng vai trò trạng thái

Nếu bạn thấy enum (kiểu liệt kê) là một lựa chọn mô hình hóa hiệu quả cho các Standard Types (kiểu chuẩn / kiểu phân loại nghiệp vụ) và/hoặc State objects (đối tượng trạng thái), bạn sẽ cần giải pháp để lưu trữ chúng. Với Hibernate, các enum trong Java đòi hỏi một kỹ thuật lưu trữ chuyên biệt. Đáng tiếc là cho đến nay, cộng đồng phát triển Hibernate vẫn chưa hỗ trợ sẵn enum như một kiểu thuộc tính mặc định (out-of-the-box). Do đó, để lưu trữ enum trong mô hình của mình, chúng ta buộc phải tạo một Hibernate custom user type.

Hãy nhớ lại rằng mỗi `GroupMember` đều sở hữu một `GroupMemberType`:

```java
public final class GroupMember extends IdentifiedValueObject {
    private String name;
    private TenantId tenantId;
    private GroupMemberType type;

    public GroupMember(
            TenantId aTenantId,
            String aName,
            GroupMemberType aType) {
        this();
        this.setName(aName);
        this.setTenantId(aTenantId);
        this.setType(aType);
        this.initialize();
    }
    ...
}

```

Các Standard Types dạng enum của `GroupMemberType` bao gồm `GROUP` và `USER`. Dưới đây là định nghĩa của nó:

```java
package com.saasovation.identityaccess.domain.model.identity;

public enum GroupMemberType {
    GROUP {
        public boolean isGroup() {
            return true;
        }
    },
    USER {
        public boolean isUser() {
            return true;
        }
    };

    public boolean isGroup() {
        return false;
    }

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000273_70c43d99f11017c5871d4663fa14a17c0093085b2334f73f5071c2f3a7bb484c.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000274_d3f88ff63ab6e306e11a14064b6f05926b42fbfeb40ac978a7148b0d1ed61592.png)

```java
    public boolean isUser() {
        return false;
    }
}

```

Câu trả lời đơn giản nhất để lưu trữ một Java enum Value là lưu biểu diễn văn bản của nó. Tuy nhiên, câu trả lời đơn giản này lại dẫn tới việc triển khai một kỹ thuật phức tạp hơn đôi chút: tạo một Hibernate custom user type. Thay vì liệt kê toàn bộ các cách tiếp cận khác nhau đối với lớp `EnumUserType` do cộng đồng Hibernate cung cấp tại đây, tôi xin dẫn lại liên kết bài viết wiki: [http://community.jboss.org/wiki/Java5EnumUserType](http://community.jboss.org/wiki/Java5EnumUserType).

Tại thời điểm viết cuốn sách này, bài viết wiki trên đã cung cấp rất nhiều giải pháp đa dạng. Có các mẫu triển khai một lớp custom user type riêng cho từng kiểu enum; cách sử dụng các parameterized type (kiểu tham số hóa) của Hibernate 3 để tránh phải viết custom user type cho từng enum (rất đáng dùng); giải pháp hỗ trợ không chỉ chuỗi ký tự mà cả biểu diễn dạng số cho giá trị enum; và thậm chí là một bản triển khai nâng cao của Gavin King. Bản triển khai nâng cao của Gavin King cho phép sử dụng enum làm type discriminator (cột phân biệt kiểu dữ liệu) hoặc làm identity (`id`) cho bảng dữ liệu.

Lựa chọn một trong số các phương án trên, dưới đây là ví dụ minh họa cách ánh xạ enum `GroupMemberType`:

```xml
<hibernate-mapping>
    <class name="com.saasovation.identityaccess.domain.model.identity.GroupMember" table="tbl_group_member" lazy="true">
        ...
        <property name="type" column="type" type="com.saasovation.identityaccess.infrastructure.persistence.GroupMemberTypeUserType" update="true" insert="true" not-null="true" />
    </class>
</hibernate-mapping>

```

Hãy lưu ý rằng thuộc tính `type` của thẻ `<property>` được trỏ tới classpath đầy đủ của lớp `GroupMemberTypeUserType`. Đây chỉ là một phương án, và bạn hoàn toàn có thể chọn bất kỳ phương án nào mình thấy phù hợp. Nhắc lại rằng định nghĩa bảng MySQL có chứa cột để lưu trữ enum này:

```sql
CREATE TABLE `tbl_group_member` (
    ...
    `type` varchar(5) NOT NULL,
    ...
) ENGINE=InnoDB;

```

Cột `type` có kiểu `VARCHAR` với dung lượng tối đa 5 ký tự, vừa đủ để lưu biểu diễn văn bản dài nhất của kiểu: `GROUP` hoặc `USER`.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000275_82f14fa1d60393c419b5d372257c673919df050174e9ef90d19942e6f7057329.png)

## Tổng kết

Trong chương này, bạn đã thấy được tầm quan trọng của việc ưu tiên sử dụng Value Object bất cứ khi nào có thể, bởi vì chúng đơn giản là dễ phát triển, kiểm thử và bảo trì hơn.

* Bạn đã nắm được các đặc tính của Value Object và cách ứng dụng chúng.
* Bạn đã thấy cách tận dụng Value Object để giảm thiểu độ phức tạp khi tích hợp hệ thống.
* Bạn đã tìm hiểu việc sử dụng các Standard Types của miền nghiệp vụ được thể hiện dưới dạng Value và nắm được một số chiến lược triển khai chúng.
* Bạn đã hiểu lý do tại sao SaaSOvation hiện ưu tiên mô hình hóa bằng Value bất cứ khi nào có thể.
* Bạn đã tích lũy kinh nghiệm về cách kiểm thử, triển khai và lưu trữ bền vững các kiểu Value thông qua các dự án thực tế của SaaSOvation.

Tiếp theo, chúng ta sẽ tìm hiểu về Domain Services, các thao tác phi trạng thái (stateless operations) thực sự là một phần cốt lõi của mô hình miền.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000276_db5159855d913c7fc2bd1ccb6c1e9d7da0a98091ab5c6698292c3340602cc5fc.png)

Trang này cố ý để trống

## Chương 7

## Services

Đôi khi, nó đơn giản không phải là một "vật thể". - Eric Evans

Một Service trong miền nghiệp vụ là một thao tác không lưu trạng thái (stateless) nhằm thực thi một nhiệm vụ đặc thù của miền. Thông thường, dấu hiệu rõ ràng nhất cho thấy bạn nên tạo một Service trong domain model là khi thao tác cần thực hiện có cảm giác không tự nhiên hoặc lạc lõng nếu đặt làm một phương thức trên Aggregate (Chương 10) hay Value Object (Chương 6). Để giải tỏa cảm giác gượng gạo đó, xu hướng tự nhiên của chúng ta có thể là tạo một phương thức tĩnh (static method) trên lớp Aggregate Root (thực thể gốc của Aggregate). Tuy nhiên, khi áp dụng DDD, chiến thuật đó là một code smell (dấu hiệu cảnh báo mã nguồn có vấn đề về thiết kế) rất có thể đang chỉ ra rằng bạn cần dùng một Service để thay thế.

## Lộ trình nội dung chương này

* Thấy được việc tinh chỉnh domain model có thể dẫn đến việc nhận ra sự cần thiết của một Service như thế nào.
* Hiểu rõ bản chất một Service trong miền nghiệp vụ là gì, và nó không phải là gì.
* Cân nhắc sự thận trọng cần thiết khi quyết định có nên tạo một Service hay không.
* Khám phá cách mô hình hóa các Service trong một miền thông qua hai ví dụ từ các dự án của SaaSOvation.

Mã nguồn bốc mùi (code smell)? Đó chính xác là những gì các lập trình viên của SaaSOvation đã trải qua sau khi refactor (tái cấu trúc) một Aggregate. Hãy cùng xem xét cách họ điều chỉnh chiến thuật. Đây là những gì đã diễn ra . . .

Vào giai đoạn đầu của dự án, nhóm đã mô hình hóa collection các thể hiện `BacklogItem` như một phần cấu thành nội bộ (composed Aggregate part) của `Product`. Cách mô hình hóa đó cho phép việc tính toán tổng giá trị ưu tiên nghiệp vụ (business priority value) của tất cả các hạng mục backlog trong sản phẩm trở thành một phương thức thể hiện (instance method) đơn giản trên lớp `Product`:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000277_5efcaed0a0080218e7581abfe2a45bc3ab4a16788f2596a0831e4391029e3209.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000278_3088a0c360c1f501d32d5140640565989bc9171ee3e235a84a90707890309d8c.png)

```java
public class Product extends ConcurrencySafeEntity {
    ...
    private Set<BacklogItem> backlogItems;
    ...
    public BusinessPriorityTotals businessPriorityTotals() {
        ...
    }
    ...
}

```

Tại thời điểm đó, thiết kế này hoàn toàn hợp lý vì phương thức `businessPriorityTotals()` chỉ việc lặp qua các thể hiện `BacklogItem` cấu thành bên trong và tính ra tổng mức ưu tiên nghiệp vụ được truy vấn. Thiết kế đã trả lời truy vấn một cách chuẩn xác bằng một Value Object, cụ thể là `BusinessPriorityTotals`.

Tuy nhiên, cấu trúc này không duy trì lâu. Như phân tích trong Chương 10 (Aggregates) chỉ ra, cụm đối tượng lớn `Product` cần phải được phân tách nhỏ ra, và `BacklogItem` được thiết kế lại để đứng độc lập thành một Aggregate riêng biệt. Do đó, thiết kế cũ sử dụng một phương thức thể hiện không còn phát huy tác dụng nữa.

Vì `Product` không còn chứa collection `BacklogItem` bên trong, phản xạ đầu tiên của nhóm là tái cấu trúc phương thức thể hiện hiện có để sử dụng `BacklogItemRepository` mới nhằm lấy tất cả các thể hiện `BacklogItem` cần cho phép tính. Liệu cách làm đó có đúng đắn không?

Thực tế, lập trình viên cố vấn cấp cao (senior mentor) đã thuyết phục cả nhóm không làm như vậy. Theo quy tắc kinh nghiệm (rule of thumb), chúng ta nên cố gắng tránh tối đa việc gọi các Repository (kho lưu trữ đối tượng miền, Chương 12) từ bên trong các Aggregate nếu có thể. Vậy còn phương án chuyển chính phương thức đó thành phương thức `static` trên lớp `Product` và truyền collection các thể hiện `BacklogItem` mà phương thức static đó cần vào danh sách tham số thì sao? Bằng cách này, phương thức gần như giữ nguyên vẹn, ngoại trừ có thêm tham số mới:

```java
public class Product extends ConcurrencySafeEntity {
    ...
    public static BusinessPriorityTotals businessPriorityTotals(
            Set<BacklogItem> aBacklogItems) {
        ...
    }
    ...
}

```

Liệu `Product` có thực sự là nơi phù hợp nhất để đặt phương thức static này? Thật khó để xác định nó thực sự thuộc về đâu. Vì thao tác này trên thực tế chỉ sử dụng các giá trị ưu tiên nghiệp vụ của từng `BacklogItem`, có lẽ phương thức static nên đặt ở đó chăng? Dù vậy, giá trị ưu tiên nghiệp vụ đang cần tìm kiếm lại là của một sản phẩm, chứ không phải của một hạng mục backlog riêng rẽ. Thật tiến thoái lưỡng nan.

Đúng lúc đó, lập trình viên cấp cao cố vấn đã lên tiếng. Anh chỉ ra rằng toàn bộ nguồn cơn của sự lúng túng này có thể được giải quyết triệt để chỉ bằng một công cụ mô hình hóa duy nhất: Domain Service. Giải pháp đó sẽ vận hành như thế nào?

Trước hết chúng ta hãy cùng thiết lập một số kiến thức nền tảng. Sau đó, chúng ta sẽ quay lại tình huống mô hình hóa này để xem nhóm đã quyết định làm gì.

## Bản chất của Domain Service (và trước hết, nó không phải là gì)

Khi nghe thấy từ *service* (dịch vụ) trong ngữ cảnh phần mềm, chúng ta thường có xu hướng liên tưởng tự nhiên đến một thành phần hạt thô (coarse-grained component) cho phép một client từ xa tương tác với một hệ thống nghiệp vụ phức tạp. Về cơ bản, điều đó mô tả một service trong SOA (Service-Oriented Architecture - Kiến trúc hướng dịch vụ, Chương 4). Có nhiều công nghệ và cách tiếp cận khác nhau để phát triển các dịch vụ SOA. Rút cuộc, các loại dịch vụ này tập trung vào RPC (Remote Procedure Call - lời gọi thủ tục từ xa) ở cấp độ hệ thống hoặc MoM (Message-Oriented Middleware - phần mềm trung gian hướng thông điệp), nơi các hệ thống khác xuyên suốt trung tâm dữ liệu hoặc trên toàn cầu có thể tương tác với dịch vụ để thực hiện các giao dịch kinh doanh.

Không có điều nào trong số đó là một Domain Service (dịch vụ miền, xử lý logic nghiệp vụ phi trạng thái).

Hơn nữa, đừng nhầm lẫn Domain Service với một Application Service (dịch vụ tầng ứng dụng - điều phối luồng xử lý không chứa logic nghiệp vụ). Chúng ta không bao giờ muốn đặt logic nghiệp vụ trong một Application Service, nhưng chúng ta lại rất muốn logic nghiệp vụ được đặt bên trong một Domain Service. Nếu bạn còn băn khoăn về sự khác biệt này, hãy đối chiếu với Chương 14 (Application). Tóm lại, để phân biệt hai khái niệm: Application Service, với tư cách là một client tự nhiên của domain model, thông thường sẽ là client gọi tới Domain Service. Bạn sẽ thấy điều đó được chứng minh ở phần sau của chương.

Chỉ vì một Domain Service có chứa từ *service* trong tên gọi không có nghĩa là nó bắt buộc phải là một thao tác giao dịch hạt thô, có khả năng gọi từ xa và nặng nề [^1].

## Tư duy Cao bồi (Cowboy Logic)

LB: "Luôn quan sát thật kỹ thứ mình chuẩn bị ăn. Biết nó *là cái gì* không quan trọng bằng việc biết chắc nó *từng là cái gì*."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000279_53eae23f4fa8c83fd4c8a4dd1c4786fe775d1b40a1927e4209d0153d67342ed0.png)

> 💡 **Giải thích thêm:** Câu thoại châm biếm này mượn hình ảnh cuộc sống hoang dã của các chàng cao bồi để nhấn mạnh tầm quan trọng của nguồn gốc bản chất. Trong phần mềm, khi tiếp cận một thành phần mang tên "Service", điều tối quan trọng là bạn phải hiểu rõ bản chất cốt lõi của nó xuất phát từ tầng nào (hạ tầng, ứng dụng hay nghiệp vụ thuần túy), thay vì chỉ nhìn vào cái nhãn "Service" chung chung mà đánh đồng cách sử dụng.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)

Các Service thuộc về miền nghiệp vụ một cách đặc thù là công cụ mô hình hóa hoàn hảo để sử dụng khi nhu cầu của bạn chạm đúng điểm tối ưu (sweet spot) của chúng. Vậy thì, sau khi đã biết Domain Service *không phải là gì*, chúng ta hãy cùng xem xét xem nó *là gì*.

[^1]: Đôi khi một Domain Service có liên quan đến việc gọi từ xa tới một Bounded Context (ngữ cảnh giới hạn trong DDD, Chương 2) bên ngoài. Tuy nhiên, trọng tâm ở đây lại khác: bản thân Domain Service không tự cung cấp một giao diện gọi thủ tục từ xa, mà nó đóng vai trò là một client gọi tới RPC đó.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000280_8fca4cdf3e5310e6da53f0fa8e946f65aff9e9a048acd65512bc4f6841246329.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000281_3de1b859bd7c3c5c9dd90c667be709e3743cc0bc8fc3df19bcf38be9abea9116.png)

> Đôi khi, nó đơn giản không phải là một vật thể. . . . Khi một quy trình hay sự biến đổi quan trọng trong miền nghiệp vụ không thuộc về trách nhiệm tự nhiên của một ENTITY hay VALUE OBJECT, hãy thêm một thao tác vào mô hình dưới dạng một interface độc lập được khai báo là SERVICE. Hãy định nghĩa interface đó theo thuật ngữ của ngôn ngữ mô hình và đảm bảo tên thao tác là một phần của UBIQUITOUS LANGUAGE (ngôn ngữ chung / ngôn ngữ toàn hiện giữa lập trình viên và chuyên gia nghiệp vụ). Hãy biến SERVICE đó thành phi trạng thái (stateless). [Evans, tr. 104, 106]

Vì domain model nhìn chung xử lý các hành vi có độ chi tiết mịn hơn (finer-grained) tập trung vào một khía cạnh cụ thể của bài toán kinh doanh đang giải quyết, một Service trong miền cũng có xu hướng tuân thủ các nguyên lý tương tự. Do nó có thể phải thao tác với nhiều đối tượng miền trong một giao dịch đơn lẻ mang tính nguyên tử (atomic), nó có đủ không gian để mở rộng độ phức tạp lên một chút.

Trong những điều kiện nào thì một thao tác sẽ không thuộc về một Entity (Chương 5) hay Value Object hiện có? Rất khó để đưa ra một danh sách đầy đủ tất cả các lý do, nhưng tôi liệt kê một vài trường hợp phổ biến ở đây. Bạn có thể sử dụng một Domain Service để:

* Thực hiện một quy trình nghiệp vụ quan trọng
* Chuyển đổi một đối tượng miền từ dạng cấu thành này sang dạng cấu thành khác
* Tính toán một Value đòi hỏi đầu vào từ nhiều hơn một đối tượng miền

Trường hợp cuối cùng — một phép tính toán — có thể xếp vào nhóm "quy trình quan trọng", nhưng tôi tách riêng ra để nêu bật sự rõ ràng. Đây là tình huống cực kỳ phổ biến, và kiểu thao tác đó có thể đòi hỏi hai, hoặc thậm chí nhiều Aggregate khác nhau (hoặc các thành phần cấu thành của chúng) làm đầu vào. Và khi việc đặt phương thức lên bất kỳ một Entity hay Value nào đều trở nên hết sức gượng gạo, giải pháp tối ưu nhất là định nghĩa một Service. Hãy đảm bảo Service đó là stateless và sở hữu một interface thể hiện rõ nét Ubiquitous Language (Chương 1) trong Bounded Context của nó.

## Hãy chắc chắn rằng bạn thực sự cần một Service

Đừng lạm dụng hoặc quá thiên vị việc mô hình hóa một khái niệm miền thành Service. Chỉ làm điều đó khi hoàn cảnh thực sự phù hợp. Nếu không cẩn thận, chúng ta có thể bắt đầu coi Service như một "viên đạn bạc" (silver bullet) trong mô hình hóa. Việc sử dụng Service một cách thái quá thường dẫn đến hậu quả tiêu cực là tạo ra một Anemic Domain Model (mô hình miền thiếu máu - chỉ có dữ liệu getter/setter mà thiếu logic nghiệp vụ) [Fowler, Anemic], nơi toàn bộ logic nghiệp vụ bị dồn vào các Service thay vì được phân bổ chủ yếu trên các Entity và Value Object. Phân tích sau đây sẽ chứng minh tầm quan trọng của việc suy nghĩ thấu đáo về các chiến thuật bạn nên áp dụng cho từng tình huống mô hình hóa. Tuân theo hướng dẫn này sẽ giúp bạn đưa ra những quyết định đúng đắn về việc có nên tạo một Service hay không.

> 💡 **Giải thích thêm:** Khái niệm "viên đạn bạc" (silver bullet) bắt nguồn từ văn hóa dân gian phương Tây (vũ khí duy nhất tiêu diệt được người sói), được Frederick Brooks đưa vào ngành phần mềm qua bài tiểu luận kinh điển "No Silver Bullet". Nó ám chỉ sự ảo tưởng rằng có một công nghệ hay mô thức thiết kế kỳ diệu nào đó có thể giải quyết được mọi vấn đề phức tạp trong lập trình chỉ bằng một đòn duy nhất.
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/No_Silver_Bullet](https://en.wikipedia.org/wiki/No_Silver_Bullet)

Chúng ta hãy cùng xem xét một ví dụ về việc nhận diện nhu cầu cần mô hình hóa một Service. Hãy nghĩ đến bài toán xác thực một `User` trong Identity and Access Context của chúng ta.

Nhớ lại rằng trong Chương 5 (Entities), chúng ta đã bắt gặp kịch bản nghiệp vụ này mà khi đó nhóm muốn hoãn lại:

* Người dùng (User) của hệ thống phải được xác thực, nhưng chỉ có thể được xác thực nếu tenant (đơn vị thuê bao/khách hàng doanh nghiệp) đang hoạt động (active).

Hãy cùng phân tích lý do tại sao một Service lại cần thiết. Liệu chúng ta có thể đặt hành vi này trực tiếp lên một Entity không? Dưới góc nhìn của client, có lẽ chúng ta có thể mô hình hóa việc xác thực như thế này:

```java
// client tìm User và yêu cầu User tự xác thực chính nó

```

```java
boolean authentic = false;
User user = DomainRegistry
    .userRepository()
    .userWithUsername(aTenantId, aUsername);
if (user != null) {
    authentic = user.isAuthentic(aPassword);
}
return authentic;

```

Tôi nhận thấy có ít nhất vài vấn đề với thiết kế này. Chúng ta đang bắt các client phải hiểu thế nào là xác thực. Chúng phải tìm kiếm `User` rồi hỏi `User` xem mật khẩu đưa vào có khớp với mật khẩu mà `User` đang nắm giữ hay không. Ngoài ra, Ubiquitous Language không được mô hình hóa một cách tường minh. Ở đây chúng ta hỏi `User` xem nó "có hợp lệ hay không" (`isAuthentic`) thay vì yêu cầu mô hình "xác thực" (`authenticate`). Nếu có thể, tốt nhất là nên mô hình hóa theo các cách diễn đạt tự nhiên mà nhóm trao đổi hàng ngày, thay vì ép nhóm phải thay đổi cách nhìn vốn tự nhiên chỉ vì chúng ta thất bại trong việc mô hình hóa khái niệm đó tốt hơn. Nhưng vẫn còn những vấn đề tồi tệ hơn thế.

Đoạn mã trên không mô hình hóa đúng những gì nhóm đã phát hiện về quy trình xác thực người dùng. Một thiếu sót nghiêm trọng là không hề có bước kiểm tra xem tenant có đang hoạt động hay không. Theo yêu cầu nghiệp vụ, nếu tenant mà người dùng trực thuộc không hoạt động, người dùng đó không được phép xác thực. Có lẽ chúng ta có thể giải quyết vấn đề như sau:

```java
// có lẽ cách này sẽ tốt hơn ...
boolean authentic = false;

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000282_f41929a92c28d458e3360183303f0fc37ba75cc4cefdd3f4e34aeda97c4a4afb.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000283_d27867a57f0c916a7a08acfe65a5f42434196e18cf8e4cbac1f652e6e3faa2ad.png)

```java
Tenant tenant = DomainRegistry
    .tenantRepository()
    .tenantOfId(aTenantId);
if (tenant != null && tenant.isActive()) {
    User user = DomainRegistry
        .userRepository()
        .userWithUsername(aTenantId, aUsername);
    if (user != null) {
        authentic = tenant.authenticate(user, aPassword);
    }
}
return authentic;

```

Đoạn kiểm tra này đã xác định chính xác rằng `Tenant` đang hoạt động trước khi tiếp tục quá trình xác thực. Chúng ta cũng đã loại bỏ được phương thức `isAuthentic()` khỏi `User` bằng cách đưa phương thức `authenticate()` lên `Tenant`.

Thế nhưng cách này vẫn chứa đựng nhiều vấn đề. Hãy nhìn vào gánh nặng bổ sung mà chúng ta vừa trút lên vai client. Giờ đây client cần phải hiểu biết về quy trình xác thực nhiều hơn mức nó cần thiết. Chúng ta có thể giảm tải đôi chút bằng cách kiểm tra `Tenant.isActive()` bên trong phương thức `authenticate()`, nhưng tôi cho rằng đó không phải là một mô hình tường minh. Nó cũng sinh ra một rắc rối khác: giờ đây `Tenant` lại có thể phải biết cách xử lý mật khẩu. Nhớ rằng một yêu cầu nghiệp vụ khác đã được đưa ra, dù không được nêu trực tiếp trong kịch bản xác thực:

* Mật khẩu bắt buộc phải được lưu trữ dưới dạng mã hóa, không được lưu dưới dạng văn bản rõ ràng (clear text).

Với các giải pháp đề xuất trên, dường như chúng ta liên tục tạo ra thêm sự xung đột (friction) trong mô hình. Với đề xuất mới nhất, chúng ta buộc phải chọn một trong bốn hướng đi không mấy dễ chịu sau:

1. Xử lý việc mã hóa trong `Tenant` và truyền mật khẩu đã mã hóa sang `User`. Điều này vi phạm Single Responsibility Principle (nguyên lý đơn trách nhiệm - SRP) [Martin, SRP] của `Tenant`, vốn chỉ có trách nhiệm mô hình hóa một tenant.
2. `User` có thể đã cần biết một chút về việc mã hóa vì nó phải đảm bảo mọi mật khẩu lưu trữ đều được mã hóa. Nếu vậy, hãy tạo một phương thức trên `User` biết cách xác thực khi nhận vào một mật khẩu văn bản rõ ràng. Nhưng trong trường hợp này, việc xác thực trên `Tenant` chỉ đóng vai trò như một facade (mẫu thiết kế che giấu độ phức tạp) được triển khai đầy đủ duy nhất trên `User`. Hơn nữa, `User` lại phải có một interface xác thực được bảo vệ (`protected`) để ngăn các client bên ngoài mô hình sử dụng trực tiếp.
3. `Tenant` yêu cầu `User` mã hóa mật khẩu văn bản rõ, sau đó đem so sánh với mật khẩu mà `User` đang nắm giữ. Cách này dường như có quá nhiều bước với một chuỗi phối hợp rườm rà. `Tenant` vẫn buộc phải hiểu các chi tiết của việc xác thực cho dù bản thân nó không trực tiếp thực hiện việc đó.
4. Bắt client tự mã hóa mật khẩu rồi truyền vào cho `Tenant`. Điều này lại càng chất thêm trách nhiệm lên client, trong khi lẽ ra client hoàn toàn không cần phải biết gì về nhu cầu mã hóa mật khẩu.

Không có đề xuất nào trong số này mang lại hiệu quả thực sự, và phía client vẫn bị biến thành quá phức tạp. Trách nhiệm mà chúng ta vừa trút lên client đáng lẽ phải được gói ghém một cách tinh tế bên trong mô hình miền. Những tri thức mang tính đặc thù thuần túy của miền nghiệp vụ không bao giờ được phép rò rỉ ra các client. Ngay cả khi client là một Application Service, thì thành phần đó cũng không chịu trách nhiệm về miền quản lý định danh và quyền truy cập (identity and access management).

## Tư duy Cao bồi (Cowboy Logic)

AJ: "Khi nhận ra mình đang ở dưới hố, việc đầu tiên cần làm là ngừng đào bới."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000284_5695eb29fc9d2044dda345fe736a32d6bd9c565eae8af298f28e4cb74d5f21c8.png)

> 💡 **Giải thích thêm:** "Luật về cái hố" (Law of Holes) là một câu ngạn ngữ tiếng Anh: "If you find yourself in a hole, stop digging." Trong kỹ nghệ phần mềm, điều này nhắc nhở rằng khi phát hiện một giải pháp thiết kế đang dẫn hệ thống vào ngõ cụt và tạo ra hàng loạt sự chắp vá tồi tệ, hành động khôn ngoan nhất là dừng ngay cách tiếp cận đó lại để tìm một mô thức đúng đắn, thay vì tiếp tục viết thêm code chắp vá khiến hệ thống lún sâu hơn vào nợ kỹ thuật.
> Nguồn tham khảo: [https://en.wikipedia.org/wiki/Law_of_holes](https://en.wikipedia.org/wiki/Law_of_holes)

Thực tế, trách nhiệm nghiệp vụ duy nhất mà client nên có chỉ là điều phối việc sử dụng một thao tác đặc thù duy nhất của miền, nơi xử lý toàn bộ các chi tiết còn lại của bài toán nghiệp vụ:

```java
// bên trong một client Application Service chỉ có
// trách nhiệm điều phối tác vụ duy nhất
UserDescriptor userDescriptor = DomainRegistry
    .authenticationService()

```

```java
    .authenticate(aTenantId, aUsername, aPassword);

```

Trong giải pháp đơn giản và thanh thoát này, client chỉ cần lấy một tham chiếu tới một thể hiện phi trạng thái của `AuthenticationService` rồi yêu cầu nó thực hiện `authenticate()`. Cách này đẩy toàn bộ các chi tiết về xác thực ra khỏi client Application Service và đưa trọn vẹn vào bên trong Domain Service. Bất kỳ số lượng đối tượng miền nào cũng có thể được Service sử dụng khi cần. Điều này bao gồm cả việc đảm bảo quá trình mã hóa mật khẩu được thực thi một cách phù hợp. Phía client không cần phải hiểu bất kỳ chi tiết nào trong số đó. Ubiquitous Language trong Bounded Context được đáp ứng trọn vẹn vì các thuật ngữ chuẩn mực được thể hiện bởi chính phần mềm mô hình hóa miền quản lý định danh, thay vì bị phân mảnh một nửa ở mô hình và một nửa ở client.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000285_118ad3c7d3d1fd4a15097342540e25765b336060b73f2074374290dfda1594c8.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000286_26ed82a6f2516ba6303f112359361d3669a7d60d74ea4b8a95cf520508ce7792.png)

Một Value Object, `UserDescriptor`, được trả về từ phương thức của Service. Đối tượng này nhỏ gọn và an toàn. Không giống như một `User` hoàn chỉnh, nó chỉ bao gồm một vài thuộc tính thiết yếu để tham chiếu tới một `User`:

```java
public class UserDescriptor implements Serializable {
    private String emailAddress;
    private TenantId tenantId;
    private String username;

    public UserDescriptor(
            TenantId aTenantId,
            String aUsername,
            String anEmailAddress) {
        ...
    }
    ...
}

```

Nó hoàn toàn phù hợp để lưu trữ trong một HTTP Session theo từng người dùng. Bản thân client Application Service có thể trực tiếp trả đối tượng này về cho bên gọi nó, hoặc tạo ra một đối tượng khác phù hợp hơn.

## Mô hình hóa một Service trong Miền nghiệp vụ

Tùy thuộc vào mục đích của một Domain Service, việc mô hình hóa nó có thể khá đơn giản. Bạn sẽ phải quyết định xem Service của mình có nên sở hữu một Separated Interface (mẫu thiết kế tách biệt giao diện và phần cài đặt) [Fowler, P of EAA] hay không. Nếu có, đây có thể là định nghĩa interface:

```java
package com.saasovation.identityaccess.domain.model.identity;

```

```java
public interface AuthenticationService {
    public UserDescriptor authenticate(
            TenantId aTenantId,
            String aUsername,
            String aPassword);
}

```

Interface này được khai báo trong cùng một Module (mô-đun đóng gói trong DDD, Chương 9) với các Aggregate đặc thù của định danh như `Tenant`, `User`, và `Group`. Điều đó được thực hiện vì `AuthenticationService` là một khái niệm thuộc về định danh, và chúng ta hiện đặt toàn bộ các khái niệm liên quan đến định danh vào bên trong Module `identity`. Bản thân định nghĩa interface rất đơn giản. Chỉ có một thao tác duy nhất là `authenticate()` được yêu cầu.

Một lựa chọn chúng ta phải đưa ra là đặt lớp cài đặt (implementation class) ở đâu. Nếu bạn đang áp dụng Dependency Inversion Principle (nguyên lý đảo ngược phụ thuộc, Chương 4) hoặc Hexagonal Architecture (kiến trúc lục giác, Chương 4), bạn có thể quyết định đặt lớp cài đặt mang tính kỹ thuật này ở một vị trí bên ngoài domain model. Ví dụ, các cài đặt kỹ thuật có thể được đặt trong một Module thuộc Infrastructure Layer (tầng hạ tầng).

Dưới đây là lớp cài đặt đó:

```java
package com.saasovation.identityaccess.infrastructure.services;

import com.saasovation.identityaccess.domain.model.DomainRegistry;
import com.saasovation.identityaccess.domain.model.identity.AuthenticationService;
import com.saasovation.identityaccess.domain.model.identity.Tenant;
import com.saasovation.identityaccess.domain.model.identity.TenantId;
import com.saasovation.identityaccess.domain.model.identity.User;
import com.saasovation.identityaccess.domain.model.identity.UserDescriptor;

public class DefaultEncryptionAuthenticationService implements AuthenticationService {
    public DefaultEncryptionAuthenticationService() {
        super();
    }

    @Override
    public UserDescriptor authenticate(
            TenantId aTenantId,
            String aUsername,
            String aPassword) {
        if (aTenantId == null) {
            throw new IllegalArgumentException(
                "TenantId must not be null.");
        }
        if (aUsername == null) {
            throw new IllegalArgumentException(
                "Username must not be null.");
        }
        if (aPassword == null) {
            throw new IllegalArgumentException(
                "Password must not be null.");
        }

        UserDescriptor userDescriptor = null;

```

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000287_d0ceb5def829065a0a7576913fccaa89dfe4ba9720abef47b7701ecd6b12beec.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000288_f9eb514bc8a112d62311383dfedd4f0ac44e48dedd69da2c47b435e325cc81b7.png)

```java
        Tenant tenant = DomainRegistry
            .tenantRepository()
            .tenantOfId(aTenantId);
        if (tenant != null && tenant.isActive()) {
            String encryptedPassword = DomainRegistry
                .encryptionService()
                .encryptedValue(aPassword);
            User user = DomainRegistry
                .userRepository()
                .userFromAuthenticCredentials(
                    aTenantId,
                    aUsername,
                    encryptedPassword);
            if (user != null && user.isEnabled()) {
                userDescriptor = user.userDescriptor();
            }
        }
        return userDescriptor;
    }
}

```

Phương thức này thực hiện kiểm tra chặt chẽ để phòng ngừa các tham số `null`. Ngoài ra, nếu quá trình xác thực thất bại trong các điều kiện thông thường, đối tượng `UserDescriptor` trả về sẽ mang giá trị `null`.

Để xác thực, chúng ta bắt đầu bằng cách cố gắng lấy `Tenant` từ Repository của nó thông qua định danh. Nếu `Tenant` vừa tồn tại vừa đang hoạt động, tiếp theo chúng ta sẽ mã hóa mật khẩu dạng văn bản rõ. Chúng ta thực hiện việc đó ngay lúc này vì mật khẩu đã mã hóa sẽ được dùng để truy vấn `User`. Thay vì chỉ yêu cầu `User` dựa trên `TenantId` và `username` trùng khớp, chúng ta còn lọc khớp trên cả mật khẩu đã mã hóa. (Kết quả mã hóa luôn luôn cho ra cùng một giá trị đối với hai mật khẩu văn bản rõ giống hệt nhau). Repository được thiết kế để lọc trên cả ba điều kiện này.

Nếu người dùng đã nhập chính xác định danh tenant, username và mật khẩu dạng văn bản rõ, thao tác này sẽ truy xuất thành công thể hiện `User` tương ứng. Tuy nhiên, điều này vẫn chưa chứng minh đầy đủ tính hợp lệ của người dùng. Vẫn còn một yêu cầu cuối cùng chưa được xử lý:

* Người dùng chỉ có thể được xác thực nếu họ đang được kích hoạt (enabled).

Ngay cả khi Repository tìm thấy thể hiện `User` thỏa mãn điều kiện lọc, tài khoản đó có thể đã bị vô hiệu hóa (disabled). Việc cung cấp khả năng vô hiệu hóa một `User` cho phép tenant kiểm soát việc xác thực người dùng ở một cấp độ khác. Do đó, ở bước cuối cùng, thể hiện `User` phải vừa khác null vừa phải đang ở trạng thái enabled, khi đó một `UserDescriptor` mới được trích xuất từ `User`.

## Separated Interface có phải là điều bắt buộc?

Vì `AuthenticationService` này không có một cài đặt kỹ thuật nặng nề, liệu việc tạo ra một Separated Interface cùng một lớp triển khai nằm ở các Layer và Module tách biệt có thực sự cần thiết? Thực tế là không, đó không phải là một điều bắt buộc tuyệt đối. Chúng ta hoàn toàn có thể tạo Service cụ thể này chỉ với một lớp triển khai duy nhất mang chính tên của Service:

```java
package com.saasovation.identityaccess.domain.model.identity;

public class AuthenticationService {
    public AuthenticationService() {
        super();
    }

    public UserDescriptor authenticate(
            TenantId aTenantId,
            String aUsername,
            String aPassword) {
        ...
    }
}

```

Sẽ chẳng có vấn đề gì sai sót với cách làm này. Bạn thậm chí có thể coi đây là cách tiếp cận phù hợp hơn vì Service cụ thể này có thể sẽ không bao giờ cần có nhiều bản triển khai khác nhau. Tuy nhiên, xét đến việc các tenant khác nhau sau này có thể mong muốn các tiêu chuẩn bảo mật chuyên biệt, việc tồn tại nhiều bản triển khai là hoàn toàn có thể xảy ra. Dù vậy, tại thời điểm hiện tại, nhóm đã quyết định bỏ việc dùng Separated Interface và sử dụng lớp như minh họa ở trên.

## Đặt tên cho Lớp Cài đặt của bạn

Trong thế giới Java, việc đặt tên cho lớp cài đặt bằng cách lấy tên của interface làm tiền tố và thêm hậu tố `Impl` đã trở nên rất phổ biến. Trong ví dụ của chúng ta, cách làm đó sẽ tạo ra cái tên `AuthenticationServiceImpl`. Hơn nữa, interface và lớp triển khai thường được đặt chung trong cùng một package. Liệu đây có phải là một điều tốt?

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000289_50b7218c160aa8a0bb3083b804581eb1355eeda3b6d97af2584b9e1d5fb51064.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000290_205977bb955c81b73cc1e605c01a67b0be466d4c395276add49f80da6b47548b.png)

Thực tế, nếu lớp cài đặt của bạn được đặt tên theo cách này, đó có lẽ là dấu hiệu rất rõ ràng cho thấy bạn không hề cần đến một Separated Interface, hoặc bạn cần phải suy nghĩ cẩn trọng hơn về tên của lớp cài đặt. Vì vậy, câu trả lời là không, cái tên `AuthenticationServiceImpl` không thực sự là một cái tên tốt. Nhưng xét lại thì cái tên `DefaultEncryptionAuthenticationService` cũng chẳng hữu ích hơn là bao. Chính vì lý do đó, nhóm SaaSOvation đã quyết định loại bỏ Separated Interface ở thời điểm này và chỉ sử dụng `AuthenticationService` như một lớp thông thường.

Nếu lớp cài đặt của bạn phục vụ các mục tiêu tách rời (decoupling) cụ thể vì bạn cung cấp nhiều bản triển khai chuyên biệt khác nhau, hãy đặt tên lớp theo đúng đặc tính chuyên biệt của nó. Nhu cầu phải đặt tên cẩn thận cho từng bản triển khai chuyên biệt chính là bằng chứng cho thấy các đặc tính chuyên biệt đó thực sự tồn tại trong miền nghiệp vụ của bạn.

Một số người sẽ kết luận rằng việc đặt tên interface và lớp cài đặt tương tự nhau giúp việc duyệt và điều hướng các package lớn chứa các cặp này trở nên dễ dàng hơn. Tuy nhiên, những người khác lại cho rằng các package cồng kềnh như vậy đã được thiết kế kém theo các mục tiêu của Module. Hơn thế nữa, những ai hướng tới các mục tiêu mô-đun hóa tập trung cũng sẽ ủng hộ việc đặt interface và các lớp cài đặt khác nhau vào các package riêng biệt, tương tự như cách chúng ta áp dụng với Dependency Inversion Principle (Chương 4). Ví dụ, interface `EncryptionService` nằm trong domain model, trong khi `MD5EncryptionService` lại cư trú ở tầng hạ tầng (infrastructure).

Việc loại bỏ Separated Interface đối với các Domain Service phi kỹ thuật sẽ không làm giảm khả năng kiểm thử (testability), vì bất kỳ interface nào mà Service phụ thuộc vào đều có thể được inject (tiêm) hoặc resolve (phân giải) thông qua một Service Factory cấu hình riêng cho việc test, hoặc bạn có thể truyền các thể hiện phụ thuộc đầu vào và đầu ra dưới dạng tham số khi cần. Hãy nhớ rằng các Service phi kỹ thuật mang tính đặc thù của miền, chẳng hạn như các phép tính toán, bắt buộc phải được kiểm thử tính đúng đắn.

Rõ ràng đây là một chủ đề gây nhiều tranh cãi, và tôi biết rằng có một bộ phận lớn lập trình viên thường xuyên đặt tên các lớp triển khai interface bằng hậu tố `Impl`. Bạn chỉ cần nhận thức rằng luôn có một luồng quan điểm đối lập hoàn toàn nhưng sở hữu các lập luận rất vững chắc để tránh cách làm đó. Như mọi khi, quyền lựa chọn hoàn toàn thuộc về bạn.

Việc sử dụng Separated Interface có thể nghiêng về vấn đề phong cách cá nhân nhiều hơn trong những trường hợp Service thuần túy thuộc về miền nghiệp vụ và sẽ không bao giờ có một triển khai kỹ thuật hay nhiều triển khai khác nhau. Như Fowler [Fowler, P of EAA] đã nêu, Separated Interface hữu ích nếu bạn có các mục tiêu tách rời nhất định: "Một client phụ thuộc vào interface có thể hoàn toàn không cần biết gì về lớp cài đặt." Tuy nhiên, nếu bạn đang sử dụng Dependency Injection (tiêm phụ thuộc) hoặc một Factory (mẫu thiết kế nhà máy tạo đối tượng) [Gamma et al.] dành cho Service, ngay cả khi interface và lớp triển khai của Service được gộp chung làm một, bạn vẫn có thể ngăn client không cần phải biết về bản cài đặt cụ thể.

Nói cách khác, cách sử dụng `DomainRegistry` như một Service Factory sau đây sẽ tách biệt client khỏi việc phải biết về bản cài đặt:

```java
// registry giúp tách biệt client khỏi việc phải biết về lớp cài đặt cụ thể
UserDescriptor userDescriptor = DomainRegistry
    .authenticationService()
    .authenticate(aTenantId, aUsername, aPassword);

```

Hoặc nếu bạn đang sử dụng Dependency Injection, bạn cũng có thể đạt được những lợi ích tương tự:

```java
public class SomeApplicationService ... {
    @Autowired
    private AuthenticationService authenticationService;
    ...
}

```

Inversion-of-control container (vùng chứa đảo ngược điều khiển, chẳng hạn như Spring) sẽ tự động tiêm thể hiện của Service vào. Vì client không bao giờ trực tiếp khởi tạo Service bằng toán tử `new`, nó hoàn toàn không cần bận tâm liệu interface và lớp cài đặt được kết hợp hay tách rời.

Rõ ràng, một số người rất có ác cảm với cả Service Factory lẫn Dependency Injection và thích tự thiết lập các phụ thuộc đầu vào thông qua constructor (hàm khởi tạo) hoặc truyền chúng vào dưới dạng tham số phương thức. Rút cuộc, đó là cách tường minh nhất để liên kết các thành phần phụ thuộc và giúp mã nguồn dễ kiểm thử nhất, thậm chí còn có thể coi là dễ dàng hơn so với Dependency Injection. Một số người có thể thấy việc kết hợp linh hoạt cả ba cách tùy theo tình huống là hữu ích, trong khi vẫn ưu tiên thiết lập phụ thuộc qua constructor nói chung. Nhiều ví dụ trong chương này sử dụng `DomainRegistry` để đảm bảo tính rõ ràng, dù không nhất thiết biểu thị đây là cách duy nhất được ưa chuộng. Rất nhiều mã nguồn thực tế được phân phối trực tuyến kèm theo cuốn sách này nghiêng về hướng thiết lập phụ thuộc thông qua constructor, hoặc bằng cách truyền trực tiếp các phụ thuộc vào phương thức dưới dạng tham số.

## Một quy trình tính toán

Dưới đây là một ví dụ khác, lần này lấy từ Core Domain (miền cốt lõi, Chương 2) hiện tại: Agile Project Management Context. Service này tính toán một kết quả từ các Value nằm trên một số lượng tùy ý các Aggregate thuộc một kiểu cụ thể. Ở đây, tôi nghĩ không có lý do thỏa đáng nào để sử dụng một Separated Interface, ít nhất là tại thời điểm hiện tại. Các phép tính toán luôn được thực hiện theo cùng một cách thức. Trừ khi tình huống đó thay đổi, chúng ta không nên bận tâm tách biệt interface khỏi lớp cài đặt làm gì.

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000291_b2410852bdb2700a9a033c2546c71c400d59e66095639d9564b6c9eff01b009f.png)

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000292_c698cdc379c0ab032159198b8e145eb1520075bc8c9cef7eeca06567d67a2987.png)

## Tư duy Cao bồi (Cowboy Logic)

* LB: "Con ngựa giống của tôi kiếm được 5.000 đô mỗi lượt phối (service), và đàn ngựa cái đang xếp hàng dài chờ sẵn."
* AJ: "Thế thì con ngựa đó đang ở đúng lãnh địa (domain) của nó rồi đấy."

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000293_b25b49625e45e2b7d14d2a32881bb7415c4b6a2d50e4cd403896c0b6080872b5.png)

> 💡 **Giải thích thêm:** Đoạn hội thoại này là một pha chơi chữ (pun) đầy hóm hỉnh dựa trên hai thuật ngữ phần mềm:
> 1. Từ **"service"**: Trong chăn nuôi gia súc, "service" mang nghĩa là một lượt phối giống của con đực giống; trong phần mềm, nó là một dịch vụ xử lý tác vụ.
> 2. Từ **"domain"**: Với cao bồi, "domain" là lãnh địa, giang sơn nơi con vật phát huy hết uy lực; trong kiến trúc phần mềm, "domain" là miền nghiệp vụ.
> Câu châm ngôn ngụ ý: Một hành vi chỉ phát huy tối đa giá trị và mang lại hiệu quả cao nhất khi nó được đặt vào đúng "domain" thuộc về nó.
> (Không có nguồn trích dẫn xác thực — cần tự kiểm chứng thêm)
> 
> 

Hãy nhớ lại rằng các lập trình viên của SaaSOvation ban đầu đã tạo ra các phương thức static hạt mịn trên `Product` để thực hiện các phép tính toán mong muốn. Đây là những gì đã diễn ra tiếp theo . . .

Lập trình viên cố vấn của nhóm cũng chỉ ra sự cần thiết của việc sử dụng một Domain Service thay vì một static method. Ý tưởng đằng sau Service này sẽ rất giống với thiết kế hiện tại: tính toán và trả về một thể hiện Value `BusinessPriorityTotals`. Nhưng Service này sẽ phải đảm đương thêm một chút công việc. Điều này bao gồm việc tìm kiếm toàn bộ các hạng mục backlog còn tồn đọng (outstanding backlog items) của một sản phẩm Scrum cụ thể, sau đó cộng tổng từng giá trị `BusinessPriority` riêng lẻ của chúng lại. Dưới đây là phần triển khai mã nguồn:

![Image](output/2013-Vaughn-Implementing%20Domain%20Driven%20Design_artifacts/image_000294_f2679726fd28f7f1252a31d8c7f689d90284b8fbd2eee89d4a03096a2d156f59.png)

```java
package com.saasovation.agilepm.domain.model.product;

import com.saasovation.agilepm.domain.model.DomainRegistry;
import com.saasovation.agilepm.domain.model.tenant.Tenant;

public class BusinessPriorityCalculator {
    public BusinessPriorityCalculator() {
        super();
    }

    public BusinessPriorityTotals businessPriorityTotals(
            Tenant aTenant,
            ProductId aProductId) {
        int totalBenefit = 0;
        int totalPenalty = 0;
        int totalCost = 0;
        int totalRisk = 0;

        java.util.Collection<BacklogItem> outstandingBacklogItems =
            DomainRegistry
                .backlogItemRepository()
                .allOutstandingProductBacklogItems(
                    aTenant,
                    aProductId);

```

```java
        for (BacklogItem backlogItem : outstandingBacklogItems) {
            if (backlogItem.hasBusinessPriority()) {
                BusinessPriorityRatings ratings =
                    backlogItem.businessPriority().ratings();
                totalBenefit += ratings.benefit();
                totalPenalty += ratings.penalty();
                totalCost += ratings.cost();
                totalRisk += ratings.risk();
            }
        }

        BusinessPriorityTotals businessPriorityTotals =
            new BusinessPriorityTotals(
                totalBenefit,
                totalPenalty,
                totalBenefit + totalPenalty,
                totalCost,
                totalRisk);

        return businessPriorityTotals;
    }
}

```

`BacklogItemRepository` được sử dụng để lấy tất cả các thể hiện `BacklogItem` còn tồn đọng. Một `BacklogItem` còn tồn đọng là hạng mục có trạng thái thuộc kiểu `Planned`, `Scheduled`, hoặc `Committed`, chứ không phải là `Done` hay `Removed`. Một Service trong miền hoàn toàn có thể tự do sử dụng các Repository khi cần, nhưng việc truy cập Repository từ bên trong một thể hiện Aggregate lại là một thực hành không được khuyến khích.